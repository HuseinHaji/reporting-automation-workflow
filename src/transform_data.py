"""Transform raw extracts into clean reporting base tables."""

import pandas as pd

from config import PROCESSED_FILES, RAW_FILES, ensure_directories


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    clean = customers.drop_duplicates("customer_id").copy()
    clean["onboarding_date"] = pd.to_datetime(clean["onboarding_date"], errors="coerce")
    clean["active_flag"] = clean["active_flag"].where(clean["active_flag"].isin(["Y", "N"]), "N")
    return clean


def clean_contracts(contracts: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    clean = contracts.drop_duplicates("contract_id").copy()
    clean = clean[clean["customer_id"].isin(customers["customer_id"])]
    clean["contract_start_date"] = pd.to_datetime(clean["contract_start_date"], errors="coerce")
    clean["contract_end_date"] = pd.to_datetime(clean["contract_end_date"], errors="coerce")
    clean["annual_contract_value"] = clean["annual_contract_value"].clip(lower=0)
    return clean


def clean_invoices(invoices: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    clean = invoices.drop_duplicates("invoice_id", keep="first").copy()
    clean["invoice_date"] = pd.to_datetime(clean["invoice_date"], errors="coerce")
    clean["due_date"] = pd.to_datetime(clean["due_date"], errors="coerce")
    valid = (
        clean["customer_id"].isin(customers["customer_id"])
        & clean["invoice_amount"].ge(0)
        & clean["invoice_date"].notna()
        & clean["due_date"].notna()
        & clean["due_date"].ge(clean["invoice_date"])
        & clean["status"].isin(["Open", "Paid", "Cancelled"])
    )
    return clean[valid].copy()


def clean_payments(payments: pd.DataFrame, invoices: pd.DataFrame) -> pd.DataFrame:
    clean = payments.drop_duplicates("payment_id").copy()
    clean["payment_date"] = pd.to_datetime(clean["payment_date"], errors="coerce")
    valid = clean["invoice_id"].isin(invoices["invoice_id"]) & clean["payment_amount"].ge(0) & clean["payment_date"].notna()
    return clean[valid].copy()


def clean_cases(cases: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    clean = cases.drop_duplicates("case_id").copy()
    clean["case_date"] = pd.to_datetime(clean["case_date"], errors="coerce")
    valid = clean["customer_id"].isin(customers["customer_id"]) & clean["case_date"].notna()
    return clean[valid].copy()


def build_invoice_payment_status(invoices: pd.DataFrame, payments: pd.DataFrame) -> pd.DataFrame:
    payment_summary = (
        payments.groupby("invoice_id", as_index=False)
        .agg(payment_amount=("payment_amount", "sum"), payment_date=("payment_date", "max"))
        .rename(columns={"payment_amount": "collected_amount"})
    )
    base = invoices.merge(payment_summary, on="invoice_id", how="left")
    base["collected_amount"] = base["collected_amount"].fillna(0)
    base["outstanding_amount"] = (base["invoice_amount"] - base["collected_amount"]).clip(lower=0)
    base["days_to_payment"] = (base["payment_date"] - base["invoice_date"]).dt.days
    base["reporting_month"] = base["invoice_date"].dt.to_period("M").astype(str)
    base["is_paid"] = base["collected_amount"].ge(base["invoice_amount"])
    base["is_overdue"] = base["outstanding_amount"].gt(0) & base["due_date"].lt(pd.Timestamp("2025-12-31"))
    base["paid_after_due_date"] = base["payment_date"].notna() & base["payment_date"].gt(base["due_date"])
    return base


def main() -> None:
    ensure_directories()
    customers = clean_customers(pd.read_csv(RAW_FILES["customers"]))
    contracts = clean_contracts(pd.read_csv(RAW_FILES["contracts"]), customers)
    invoices = clean_invoices(pd.read_csv(RAW_FILES["invoices"]), customers)
    payments = clean_payments(pd.read_csv(RAW_FILES["payments"]), invoices)
    cases = clean_cases(pd.read_csv(RAW_FILES["cases"]), customers)
    invoice_status = build_invoice_payment_status(invoices, payments)

    outputs = {
        "customers": customers,
        "contracts": contracts,
        "invoices": invoices,
        "payments": payments,
        "cases": cases,
        "invoice_payments": invoice_status,
    }
    for name, frame in outputs.items():
        frame.to_csv(PROCESSED_FILES[name], index=False)
        print(f"Wrote processed table {PROCESSED_FILES[name]} ({len(frame):,} rows)")


if __name__ == "__main__":
    main()
