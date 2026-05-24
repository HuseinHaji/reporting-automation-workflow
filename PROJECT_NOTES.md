# Technical Notes

## Dataset Design

The project uses a synthetic B2B financial-services style reporting dataset. Core entities are customers, invoices, payments, contracts, claims/service cases, and monthly targets. The generator intentionally creates realistic quality issues such as duplicate invoice IDs, missing customer references, negative amounts, inactive accounts with open invoices, late payments, and expired contract scenarios.

## Pipeline Architecture

```text
src/generate_synthetic_data.py
  -> data/raw/*.csv
src/validate_data.py
  -> output/audit/data_quality_report.csv
src/transform_data.py
  -> data/processed/*.csv
src/calculate_kpis.py
  -> output/reports/monthly_reporting_summary.csv
  -> output/reports/customer_reporting_table.csv
src/generate_reports.py
  -> output/exceptions/reporting_exceptions.csv
src/export_powerbi.py
  -> output/powerbi/powerbi_reporting_dashboard.csv
```

## Validation Checks

Validation rules cover required columns, duplicate primary keys, referential integrity, non-negative amounts, due dates after invoice dates, reasonable payment dates, valid status values, valid active flags, target-rate ranges, and null checks in critical fields.

Each check is written to `output/audit/data_quality_report.csv` with status, records checked, failed records, failure rate, severity, and timestamp.

## KPI Formulas

- `collection_rate = collected_amount / total_revenue`
- `overdue_rate = overdue_amount / total_revenue`
- `outstanding_amount = invoice_amount - collected_amount`
- `overdue_amount = outstanding unpaid amount after due date`
- `avg_days_to_payment = payment_date - invoice_date`
- `high_risk_customer_share = high_risk_customers / total_customers`
- `target_achievement_rate = total_revenue / target_revenue`
- `mom_revenue_change = current_month_revenue / prior_month_revenue - 1`

## Exception Logic

The exception layer translates technical data issues into business-readable reporting items. Each record has an exception type, severity, explanation, and suggested action. Covered exceptions include missing customer data, invoice without payment, overdue invoice, payment after due date, high overdue ratio, negative amount, inactive customer with open invoice, contract expired but invoice active, and duplicate invoice ID.

## SQL Layer

The `sql/` folder contains PostgreSQL-style analytics queries. They are written as portfolio examples for reporting environments and include CTEs, `CASE WHEN`, joins, date logic, aggregations, filtered aggregates, and window functions.

## Power BI Export Design

`output/powerbi/powerbi_reporting_dashboard.csv` is a flat customer-level table with monthly KPI context. It avoids unnecessary technical columns and includes dashboard-ready categories such as risk category, overdue category, collection status, exception flag, and reporting status.

## Testing Approach

Pytest coverage checks that the pipeline runs, raw and output files are created, schemas contain required columns, KPI values stay within valid ranges, duplicate IDs are removed in processed data, negative amounts are excluded from clean outputs, exception severities are valid, the data quality report is populated, and the Power BI export is not empty.

## Known Limitations

This is a portfolio implementation using CSV files and synthetic data. It does not represent a production data platform, does not use real company data, and does not claim real business impact. The design prioritizes transparency and inspectability over heavy infrastructure.

## Future Extensions

- Load raw and reporting tables into PostgreSQL.
- Add Excel workbook exports for finance and operations users.
- Add orchestration with Airflow, Prefect, or scheduled GitHub Actions.
- Add row-level source-file lineage.
- Build a Power BI dashboard and add real screenshots to `screenshots/`.
