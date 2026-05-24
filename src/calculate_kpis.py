"""Calculate management reporting KPIs from processed reporting tables."""

import pandas as pd

from config import PROCESSED_FILES, RAW_FILES, REPORT_FILES, ensure_directories


def load_processed() -> dict[str, pd.DataFrame]:
    return {
        "customers": pd.read_csv(PROCESSED_FILES["customers"]),
        "contracts": pd.read_csv(PROCESSED_FILES["contracts"]),
        "cases": pd.read_csv(PROCESSED_FILES["cases"]),
        "invoice_payments": pd.read_csv(
            PROCESSED_FILES["invoice_payments"],
            parse_dates=["invoice_date", "due_date", "payment_date"],
        ),
        "monthly_targets": pd.read_csv(RAW_FILES["monthly_targets"], parse_dates=["month"]),
    }


def build_monthly_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    invoices = data["invoice_payments"].copy()
    customers = data["customers"].copy()
    cases = data["cases"].copy()
    targets = data["monthly_targets"].copy()

    enriched = invoices.merge(customers[["customer_id", "risk_rating", "active_flag"]], on="customer_id", how="left")
    monthly = (
        enriched.groupby("reporting_month", as_index=False)
        .agg(
            total_customers=("customer_id", "nunique"),
            total_revenue=("invoice_amount", "sum"),
            collected_amount=("collected_amount", "sum"),
            outstanding_amount=("outstanding_amount", "sum"),
            overdue_amount=("is_overdue", lambda s: enriched.loc[s.index, "outstanding_amount"][s].sum()),
            avg_days_to_payment=("days_to_payment", "mean"),
            high_risk_customers=("risk_rating", lambda s: (s == "High").sum()),
        )
    )
    active_counts = (
        enriched[enriched["active_flag"] == "Y"].groupby("reporting_month")["customer_id"].nunique().rename("active_customers")
    )
    monthly = monthly.merge(active_counts, on="reporting_month", how="left")

    cases["reporting_month"] = pd.to_datetime(cases["case_date"]).dt.to_period("M").astype(str)
    case_summary = (
        cases.groupby("reporting_month", as_index=False)
        .agg(
            open_cases=("case_status", lambda s: s.isin(["Open", "In Review"]).sum()),
            closed_cases=("case_status", lambda s: (s == "Closed").sum()),
            case_amount=("case_amount", "sum"),
        )
    )
    target_summary = targets.assign(reporting_month=targets["month"].dt.to_period("M").astype(str))
    target_summary = target_summary.groupby("reporting_month", as_index=False)["target_revenue"].sum()

    monthly = monthly.merge(case_summary, on="reporting_month", how="left").merge(target_summary, on="reporting_month", how="left")
    monthly[["open_cases", "closed_cases", "case_amount"]] = monthly[["open_cases", "closed_cases", "case_amount"]].fillna(0)
    monthly["active_customers"] = monthly["active_customers"].fillna(0).astype(int)
    monthly["collection_rate"] = (monthly["collected_amount"] / monthly["total_revenue"]).fillna(0).round(4)
    monthly["overdue_rate"] = (monthly["overdue_amount"] / monthly["total_revenue"]).fillna(0).round(4)
    monthly["high_risk_customer_share"] = (monthly["high_risk_customers"] / monthly["total_customers"]).fillna(0).round(4)
    monthly["target_achievement_rate"] = (monthly["total_revenue"] / monthly["target_revenue"]).fillna(0).round(4)
    monthly["mom_revenue_change"] = monthly["total_revenue"].pct_change().fillna(0).round(4)
    monthly["avg_days_to_payment"] = monthly["avg_days_to_payment"].fillna(0).round(1)

    columns = [
        "reporting_month",
        "total_customers",
        "active_customers",
        "total_revenue",
        "collected_amount",
        "outstanding_amount",
        "overdue_amount",
        "collection_rate",
        "overdue_rate",
        "open_cases",
        "closed_cases",
        "case_amount",
        "avg_days_to_payment",
        "high_risk_customer_share",
        "target_revenue",
        "target_achievement_rate",
        "mom_revenue_change",
    ]
    return monthly[columns].sort_values("reporting_month")


def build_customer_reporting_table(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    customers = data["customers"].copy()
    invoices = data["invoice_payments"].copy()
    contracts = data["contracts"].copy()
    cases = data["cases"].copy()

    invoice_summary = (
        invoices.groupby("customer_id", as_index=False)
        .agg(
            total_invoice_amount=("invoice_amount", "sum"),
            collected_amount=("collected_amount", "sum"),
            outstanding_amount=("outstanding_amount", "sum"),
            overdue_amount=("is_overdue", lambda s: invoices.loc[s.index, "outstanding_amount"][s].sum()),
            avg_days_to_payment=("days_to_payment", "mean"),
        )
    )
    contract_summary = (
        contracts.groupby("customer_id", as_index=False)
        .agg(contract_value=("annual_contract_value", "sum"), active_contracts=("contract_status", lambda s: (s == "Active").sum()))
    )
    case_summary = (
        cases.groupby("customer_id", as_index=False).agg(open_cases=("case_status", lambda s: s.isin(["Open", "In Review"]).sum()))
    )

    report = customers.merge(invoice_summary, on="customer_id", how="left")
    report = report.merge(contract_summary, on="customer_id", how="left").merge(case_summary, on="customer_id", how="left")
    numeric_cols = [
        "total_invoice_amount",
        "collected_amount",
        "outstanding_amount",
        "overdue_amount",
        "avg_days_to_payment",
        "contract_value",
        "active_contracts",
        "open_cases",
    ]
    report[numeric_cols] = report[numeric_cols].fillna(0)
    report["overdue_ratio"] = (report["overdue_amount"] / report["total_invoice_amount"]).replace([float("inf")], 0).fillna(0)
    report["reporting_status"] = "Ready"
    report.loc[report["overdue_ratio"] > 0.30, "reporting_status"] = "Review overdue exposure"
    report.loc[(report["active_flag"] == "N") & (report["outstanding_amount"] > 0), "reporting_status"] = "Review inactive account"
    report["exception_flag"] = report["reporting_status"].ne("Ready")
    report["avg_days_to_payment"] = report["avg_days_to_payment"].fillna(0).round(1)
    report["overdue_ratio"] = report["overdue_ratio"].round(4)

    columns = [
        "customer_id",
        "customer_name",
        "country",
        "industry",
        "company_size",
        "risk_rating",
        "account_manager",
        "total_invoice_amount",
        "collected_amount",
        "outstanding_amount",
        "overdue_amount",
        "overdue_ratio",
        "avg_days_to_payment",
        "contract_value",
        "active_contracts",
        "open_cases",
        "reporting_status",
        "exception_flag",
    ]
    return report[columns].sort_values(["exception_flag", "outstanding_amount"], ascending=[False, False])


def main() -> None:
    ensure_directories()
    data = load_processed()
    monthly = build_monthly_summary(data)
    customer = build_customer_reporting_table(data)
    monthly.to_csv(REPORT_FILES["monthly_summary"], index=False)
    customer.to_csv(REPORT_FILES["customer_table"], index=False)
    print(f"KPI tables written to {REPORT_FILES['monthly_summary'].parent}")


if __name__ == "__main__":
    main()
