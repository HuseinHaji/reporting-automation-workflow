"""Run schema and data quality checks for the synthetic reporting workflow."""

from datetime import datetime
from typing import Callable

import pandas as pd

from config import (
    AUDIT_DIR,
    RAW_FILES,
    REPORT_FILES,
    VALID_ACTIVE_FLAGS,
    VALID_CASE_STATUSES,
    VALID_CONTRACT_STATUSES,
    VALID_INVOICE_STATUSES,
    ensure_directories,
)

SCHEMAS = {
    "customers": [
        "customer_id",
        "customer_name",
        "country",
        "industry",
        "company_size",
        "risk_rating",
        "account_manager",
        "onboarding_date",
        "active_flag",
    ],
    "invoices": ["invoice_id", "customer_id", "invoice_date", "due_date", "invoice_amount", "currency", "status"],
    "payments": ["payment_id", "invoice_id", "payment_date", "payment_amount", "payment_method"],
    "contracts": [
        "contract_id",
        "customer_id",
        "contract_start_date",
        "contract_end_date",
        "annual_contract_value",
        "product_line",
        "contract_status",
    ],
    "cases": ["case_id", "customer_id", "case_date", "case_type", "case_amount", "case_status"],
    "monthly_targets": ["month", "country", "product_line", "target_revenue", "target_collection_rate"],
}


def load_raw_data() -> dict[str, pd.DataFrame]:
    return {name: pd.read_csv(path) for name, path in RAW_FILES.items()}


def add_check(
    rows: list[dict[str, object]],
    check_name: str,
    table_name: str,
    records_checked: int,
    failed_records: int,
    severity: str,
) -> None:
    rows.append(
        {
            "check_name": check_name,
            "table_name": table_name,
            "status": "PASS" if failed_records == 0 else "FAIL",
            "records_checked": records_checked,
            "failed_records": int(failed_records),
            "failure_rate": round(failed_records / records_checked, 4) if records_checked else 0,
            "severity": severity,
            "check_timestamp": datetime.utcnow().isoformat(timespec="seconds"),
        }
    )


def check_required_columns(rows: list[dict[str, object]], table: str, frame: pd.DataFrame) -> None:
    missing = [column for column in SCHEMAS[table] if column not in frame.columns]
    add_check(rows, "required_columns_exist", table, len(SCHEMAS[table]), len(missing), "Critical")


def check_no_nulls(rows: list[dict[str, object]], table: str, frame: pd.DataFrame, columns: list[str]) -> None:
    existing = [column for column in columns if column in frame.columns]
    failed = int(frame[existing].isna().any(axis=1).sum()) if existing else len(frame)
    add_check(rows, "critical_fields_not_null", table, len(frame), failed, "High")


def check_duplicate_key(rows: list[dict[str, object]], table: str, frame: pd.DataFrame, key: str) -> None:
    failed = int(frame.duplicated(key, keep=False).sum()) if key in frame.columns else len(frame)
    add_check(rows, f"no_duplicate_{key}", table, len(frame), failed, "Critical")


def check_condition(
    rows: list[dict[str, object]],
    check_name: str,
    table: str,
    frame: pd.DataFrame,
    invalid_condition: Callable[[pd.DataFrame], pd.Series],
    severity: str,
) -> None:
    failed = int(invalid_condition(frame).fillna(False).sum())
    add_check(rows, check_name, table, len(frame), failed, severity)


def build_quality_report(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for table, frame in data.items():
        check_required_columns(rows, table, frame)

    customers = data["customers"]
    invoices = data["invoices"]
    payments = data["payments"]
    contracts = data["contracts"]
    cases = data["cases"]
    targets = data["monthly_targets"]

    check_duplicate_key(rows, "customers", customers, "customer_id")
    check_duplicate_key(rows, "invoices", invoices, "invoice_id")
    check_duplicate_key(rows, "payments", payments, "payment_id")
    check_duplicate_key(rows, "contracts", contracts, "contract_id")
    check_duplicate_key(rows, "cases", cases, "case_id")

    check_no_nulls(rows, "customers", customers, ["customer_id", "customer_name", "country", "risk_rating"])
    check_no_nulls(rows, "invoices", invoices, ["invoice_id", "customer_id", "invoice_date", "due_date", "invoice_amount"])
    check_no_nulls(rows, "payments", payments, ["payment_id", "invoice_id", "payment_date", "payment_amount"])
    check_no_nulls(rows, "contracts", contracts, ["contract_id", "customer_id", "contract_start_date", "contract_end_date"])
    check_no_nulls(rows, "cases", cases, ["case_id", "customer_id", "case_date", "case_status"])

    customer_ids = set(customers["customer_id"])
    invoice_ids = set(invoices["invoice_id"])
    check_condition(rows, "valid_active_flag", "customers", customers, lambda df: ~df["active_flag"].isin(VALID_ACTIVE_FLAGS), "High")
    check_condition(rows, "invoice_customer_exists", "invoices", invoices, lambda df: ~df["customer_id"].isin(customer_ids), "Critical")
    check_condition(rows, "contract_customer_exists", "contracts", contracts, lambda df: ~df["customer_id"].isin(customer_ids), "Critical")
    check_condition(rows, "case_customer_exists", "cases", cases, lambda df: ~df["customer_id"].isin(customer_ids), "High")
    check_condition(rows, "payment_invoice_exists", "payments", payments, lambda df: ~df["invoice_id"].isin(invoice_ids), "Critical")
    check_condition(rows, "invoice_amount_non_negative", "invoices", invoices, lambda df: df["invoice_amount"] < 0, "Critical")
    check_condition(rows, "payment_amount_non_negative", "payments", payments, lambda df: df["payment_amount"] < 0, "Critical")
    check_condition(
        rows,
        "due_date_after_invoice_date",
        "invoices",
        invoices,
        lambda df: pd.to_datetime(df["due_date"], errors="coerce") < pd.to_datetime(df["invoice_date"], errors="coerce"),
        "High",
    )
    check_condition(
        rows,
        "payment_date_reasonable",
        "payments",
        payments,
        lambda df: (pd.to_datetime(df["payment_date"], errors="coerce") < pd.Timestamp("2024-01-01"))
        | (pd.to_datetime(df["payment_date"], errors="coerce") > pd.Timestamp("2026-12-31")),
        "Medium",
    )
    check_condition(rows, "valid_invoice_status", "invoices", invoices, lambda df: ~df["status"].isin(VALID_INVOICE_STATUSES), "High")
    check_condition(rows, "valid_contract_status", "contracts", contracts, lambda df: ~df["contract_status"].isin(VALID_CONTRACT_STATUSES), "Medium")
    check_condition(rows, "valid_case_status", "cases", cases, lambda df: ~df["case_status"].isin(VALID_CASE_STATUSES), "Medium")
    check_condition(rows, "target_revenue_non_negative", "monthly_targets", targets, lambda df: df["target_revenue"] < 0, "High")
    check_condition(
        rows,
        "target_collection_rate_valid",
        "monthly_targets",
        targets,
        lambda df: ~df["target_collection_rate"].between(0, 1),
        "High",
    )

    return pd.DataFrame(rows)


def main() -> None:
    ensure_directories()
    data = load_raw_data()
    report = build_quality_report(data)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT_FILES["quality_report"], index=False)
    failed = int((report["status"] == "FAIL").sum())
    print(f"Data validation completed with {failed} failed checks. Report: {REPORT_FILES['quality_report']}")


if __name__ == "__main__":
    main()
