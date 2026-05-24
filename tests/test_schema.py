from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_exception_report_schema_and_severities():
    exceptions = pd.read_csv(ROOT / "output/exceptions/reporting_exceptions.csv")
    required = {
        "exception_id",
        "reporting_month",
        "customer_id",
        "exception_type",
        "severity",
        "description",
        "suggested_action",
    }

    assert required.issubset(exceptions.columns)
    assert set(exceptions["severity"]).issubset({"Low", "Medium", "High", "Critical"})
    assert not exceptions["suggested_action"].isna().any()


def test_powerbi_export_is_dashboard_ready():
    export = pd.read_csv(ROOT / "output/powerbi/powerbi_reporting_dashboard.csv")

    assert not export.empty
    assert "dashboard_refresh_note" in export.columns
    assert "risk_category" in export.columns
    assert "overdue_category" in export.columns
    assert export.columns.str.contains(" ").sum() == 0
