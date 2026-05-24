from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_full_pipeline_creates_expected_outputs():
    expected = [
        "data/raw/customers.csv",
        "data/raw/invoices.csv",
        "data/raw/payments.csv",
        "data/raw/contracts.csv",
        "data/raw/claims_or_cases.csv",
        "data/raw/monthly_targets.csv",
        "output/reports/monthly_reporting_summary.csv",
        "output/reports/customer_reporting_table.csv",
        "output/exceptions/reporting_exceptions.csv",
        "output/audit/data_quality_report.csv",
        "output/powerbi/powerbi_reporting_dashboard.csv",
    ]
    for relative_path in expected:
        path = ROOT / relative_path
        assert path.exists(), f"Missing expected output: {relative_path}"
        assert path.stat().st_size > 0, f"Output is empty: {relative_path}"
