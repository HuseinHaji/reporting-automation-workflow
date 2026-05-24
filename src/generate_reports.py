"""Create business-readable exception reports and reporting artifacts."""

import pandas as pd

from config import PROCESSED_FILES, RAW_FILES, REPORT_FILES, VALID_SEVERITIES, ensure_directories


def add_exception(
    rows: list[dict[str, object]],
    reporting_month: str,
    customer_id: str,
    exception_type: str,
    severity: str,
    description: str,
    suggested_action: str,
) -> None:
    rows.append(
        {
            "exception_id": f"EXC{len(rows) + 1:05d}",
            "reporting_month": reporting_month,
            "customer_id": customer_id,
            "exception_type": exception_type,
            "severity": severity,
            "description": description,
            "suggested_action": suggested_action,
        }
    )


def build_exceptions() -> pd.DataFrame:
    raw_customers = pd.read_csv(RAW_FILES["customers"])
    raw_invoices = pd.read_csv(RAW_FILES["invoices"], parse_dates=["invoice_date", "due_date"])
    raw_payments = pd.read_csv(RAW_FILES["payments"], parse_dates=["payment_date"])
    customers = pd.read_csv(PROCESSED_FILES["customers"])
    contracts = pd.read_csv(PROCESSED_FILES["contracts"], parse_dates=["contract_end_date"])
    invoice_status = pd.read_csv(PROCESSED_FILES["invoice_payments"], parse_dates=["invoice_date", "due_date", "payment_date"])
    customer_report = pd.read_csv(REPORT_FILES["customer_table"])

    rows: list[dict[str, object]] = []
    known_customers = set(raw_customers["customer_id"])

    duplicate_invoices = raw_invoices[raw_invoices.duplicated("invoice_id", keep=False)]
    for _, invoice in duplicate_invoices.iterrows():
        add_exception(
            rows,
            str(pd.to_datetime(invoice["invoice_date"]).to_period("M")),
            invoice["customer_id"],
            "Duplicate invoice ID",
            "Critical",
            f"Invoice {invoice['invoice_id']} appears more than once in the raw extract.",
            "Investigate source-system duplicate before publishing the monthly report.",
        )

    missing_customer = raw_invoices[~raw_invoices["customer_id"].isin(known_customers)]
    for _, invoice in missing_customer.iterrows():
        add_exception(
            rows,
            str(pd.to_datetime(invoice["invoice_date"]).to_period("M")),
            invoice["customer_id"],
            "Missing customer data",
            "Critical",
            "Invoice references a customer ID that is not available in the customer master data.",
            "Confirm customer master completeness or request corrected source extract.",
        )

    negative_invoices = raw_invoices[raw_invoices["invoice_amount"] < 0]
    for _, invoice in negative_invoices.iterrows():
        add_exception(
            rows,
            str(pd.to_datetime(invoice["invoice_date"]).to_period("M")),
            invoice["customer_id"],
            "Negative amount",
            "Critical",
            "Invoice amount is negative and cannot be included in standard revenue reporting.",
            "Review whether the record should be treated as a credit note or source-data correction.",
        )

    negative_payments = raw_payments[raw_payments["payment_amount"] < 0]
    payment_invoice_lookup = raw_invoices.drop_duplicates("invoice_id").set_index("invoice_id")["customer_id"].to_dict()
    for _, payment in negative_payments.iterrows():
        add_exception(
            rows,
            str(pd.to_datetime(payment["payment_date"]).to_period("M")),
            payment_invoice_lookup.get(payment["invoice_id"], "Unknown"),
            "Negative amount",
            "High",
            "Payment amount is negative and excluded from collection reporting.",
            "Check whether this is a reversal, adjustment, or incorrect payment extract.",
        )

    unpaid = invoice_status[invoice_status["collected_amount"] == 0]
    for _, invoice in unpaid.head(80).iterrows():
        add_exception(
            rows,
            invoice["reporting_month"],
            invoice["customer_id"],
            "Invoice without payment",
            "Medium",
            f"Invoice {invoice['invoice_id']} has no matching payment record.",
            "Review collection status and confirm whether payment is expected in a later period.",
        )

    overdue = invoice_status[invoice_status["is_overdue"]]
    for _, invoice in overdue.head(100).iterrows():
        add_exception(
            rows,
            invoice["reporting_month"],
            invoice["customer_id"],
            "Overdue invoice",
            "High",
            f"Invoice {invoice['invoice_id']} has outstanding value past the due date.",
            "Follow up with account manager and review customer payment behavior.",
        )

    late_paid = invoice_status[invoice_status["paid_after_due_date"]]
    for _, invoice in late_paid.head(80).iterrows():
        add_exception(
            rows,
            invoice["reporting_month"],
            invoice["customer_id"],
            "Payment after due date",
            "Low",
            f"Payment for invoice {invoice['invoice_id']} was received after the due date.",
            "Monitor for repeated late-payment patterns in future reporting cycles.",
        )

    high_overdue = customer_report[customer_report["overdue_ratio"] > 0.30]
    for _, customer in high_overdue.iterrows():
        add_exception(
            rows,
            "2025-12",
            customer["customer_id"],
            "High overdue ratio",
            "High",
            "Customer has overdue amount above 30% of total invoiced amount.",
            "Review payment behavior and follow up with account manager.",
        )

    inactive = customers[customers["active_flag"] == "N"][["customer_id"]]
    inactive_open = invoice_status.merge(inactive, on="customer_id", how="inner")
    inactive_open = inactive_open[inactive_open["outstanding_amount"] > 0]
    for _, invoice in inactive_open.iterrows():
        add_exception(
            rows,
            invoice["reporting_month"],
            invoice["customer_id"],
            "Inactive customer with open invoice",
            "High",
            "Inactive customer still has an open invoice in the reporting base.",
            "Confirm account status and invoice ownership before report publication.",
        )

    expired_contracts = contracts[contracts["contract_status"] == "Expired"][["customer_id", "contract_end_date"]]
    expired_active_invoices = invoice_status.merge(expired_contracts, on="customer_id", how="inner")
    expired_active_invoices = expired_active_invoices[expired_active_invoices["invoice_date"] > expired_active_invoices["contract_end_date"]]
    for _, invoice in expired_active_invoices.head(80).iterrows():
        add_exception(
            rows,
            invoice["reporting_month"],
            invoice["customer_id"],
            "Contract expired but invoice active",
            "Medium",
            "Invoice date is after the recorded contract end date.",
            "Validate contract renewal status or correct contract metadata.",
        )

    exceptions = pd.DataFrame(rows)
    if not exceptions.empty:
        exceptions = exceptions[exceptions["severity"].isin(VALID_SEVERITIES)]
    return exceptions


def main() -> None:
    ensure_directories()
    exceptions = build_exceptions()
    exceptions.to_csv(REPORT_FILES["exceptions"], index=False)
    customer = pd.read_csv(REPORT_FILES["customer_table"])
    flagged = set(exceptions["customer_id"]) if not exceptions.empty else set()
    customer["exception_flag"] = customer["customer_id"].isin(flagged) | customer["exception_flag"].astype(bool)
    customer.loc[customer["exception_flag"] & customer["reporting_status"].eq("Ready"), "reporting_status"] = "Review exceptions"
    customer.to_csv(REPORT_FILES["customer_table"], index=False)
    print(f"Exception report written with {len(exceptions):,} records: {REPORT_FILES['exceptions']}")


if __name__ == "__main__":
    main()
