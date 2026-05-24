from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_monthly_kpis_have_valid_ranges():
    monthly = pd.read_csv(ROOT / "output/reports/monthly_reporting_summary.csv")

    assert not monthly.empty
    assert monthly["collection_rate"].between(0, 1).all()
    assert monthly["overdue_rate"].between(0, 1).all()
    assert monthly["high_risk_customer_share"].between(0, 1).all()
    assert (monthly["total_revenue"] >= 0).all()
    assert (monthly["outstanding_amount"] >= 0).all()


def test_customer_reporting_table_required_columns():
    customer = pd.read_csv(ROOT / "output/reports/customer_reporting_table.csv")
    required = {
        "customer_id",
        "customer_name",
        "country",
        "industry",
        "company_size",
        "risk_rating",
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
    }

    assert required.issubset(customer.columns)
    assert customer["overdue_ratio"].between(0, 1).all()
