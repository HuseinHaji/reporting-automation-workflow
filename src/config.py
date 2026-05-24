"""Shared project configuration for the reporting automation workflow."""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REFERENCE_DIR = DATA_DIR / "reference"
OUTPUT_DIR = ROOT_DIR / "output"
REPORTS_DIR = OUTPUT_DIR / "reports"
POWERBI_DIR = OUTPUT_DIR / "powerbi"
AUDIT_DIR = OUTPUT_DIR / "audit"
EXCEPTIONS_DIR = OUTPUT_DIR / "exceptions"
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"

RANDOM_SEED = 2026
REPORTING_MONTH = "2025-12"

RAW_FILES = {
    "customers": RAW_DIR / "customers.csv",
    "invoices": RAW_DIR / "invoices.csv",
    "payments": RAW_DIR / "payments.csv",
    "contracts": RAW_DIR / "contracts.csv",
    "cases": RAW_DIR / "claims_or_cases.csv",
    "monthly_targets": RAW_DIR / "monthly_targets.csv",
}

PROCESSED_FILES = {
    "customers": PROCESSED_DIR / "customers_clean.csv",
    "invoices": PROCESSED_DIR / "invoices_clean.csv",
    "payments": PROCESSED_DIR / "payments_clean.csv",
    "contracts": PROCESSED_DIR / "contracts_clean.csv",
    "cases": PROCESSED_DIR / "claims_or_cases_clean.csv",
    "invoice_payments": PROCESSED_DIR / "invoice_payment_status.csv",
}

REPORT_FILES = {
    "monthly_summary": REPORTS_DIR / "monthly_reporting_summary.csv",
    "customer_table": REPORTS_DIR / "customer_reporting_table.csv",
    "exceptions": EXCEPTIONS_DIR / "reporting_exceptions.csv",
    "quality_report": AUDIT_DIR / "data_quality_report.csv",
    "powerbi_export": POWERBI_DIR / "powerbi_reporting_dashboard.csv",
}

VALID_RISK_RATINGS = {"Low", "Medium", "High"}
VALID_ACTIVE_FLAGS = {"Y", "N"}
VALID_INVOICE_STATUSES = {"Open", "Paid", "Cancelled"}
VALID_CONTRACT_STATUSES = {"Active", "Expired", "Pending Renewal"}
VALID_CASE_STATUSES = {"Open", "Closed", "In Review"}
VALID_SEVERITIES = {"Low", "Medium", "High", "Critical"}


def ensure_directories() -> None:
    """Create all folders used by the pipeline."""
    for path in [
        RAW_DIR,
        PROCESSED_DIR,
        REFERENCE_DIR,
        REPORTS_DIR,
        POWERBI_DIR,
        AUDIT_DIR,
        EXCEPTIONS_DIR,
        SCREENSHOTS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
