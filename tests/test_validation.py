from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_raw_primary_keys_and_amount_quality_after_cleaning():
    customers = pd.read_csv(ROOT / "data/processed/customers_clean.csv")
    invoices = pd.read_csv(ROOT / "data/processed/invoices_clean.csv")
    payments = pd.read_csv(ROOT / "data/processed/payments_clean.csv")

    assert not customers["customer_id"].duplicated().any()
    assert not invoices["invoice_id"].duplicated().any()
    assert not payments["payment_id"].duplicated().any()
    assert (invoices["invoice_amount"] >= 0).all()
    assert (payments["payment_amount"] >= 0).all()


def test_data_quality_report_has_business_controls():
    quality = pd.read_csv(ROOT / "output/audit/data_quality_report.csv")

    assert not quality.empty
    assert {"PASS", "FAIL"}.issuperset(set(quality["status"]))
    assert {
        "required_columns_exist",
        "no_duplicate_invoice_id",
        "invoice_customer_exists",
        "invoice_amount_non_negative",
        "payment_amount_non_negative",
        "due_date_after_invoice_date",
    }.issubset(set(quality["check_name"]))
