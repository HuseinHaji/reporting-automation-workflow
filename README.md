# Reporting Automation Workflow

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![SQL](https://img.shields.io/badge/SQL-PostgreSQL%20style-green)
![pandas](https://img.shields.io/badge/pandas-analytics-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-demo-red)
![Docker](https://img.shields.io/badge/Docker-ready-informational)
![Tests](https://img.shields.io/badge/pytest-covered-brightgreen)

Reporting Automation Workflow is a synthetic business reporting project that demonstrates how recurring manual reports can be automated using Python, SQL, data validation, KPI logic, exception reporting, and dashboard-ready exports.

## Business Context

A company has recurring monthly reporting built from raw business extracts. Analysts spend time collecting files, checking errors, cleaning records, calculating KPIs, preparing Excel-style outputs, and publishing dashboard-ready datasets. This portfolio implementation simulates that workflow using a synthetic reporting dataset for B2B financial services and insurance-style management reporting.

## Business Problem

Manual reporting creates repeated effort and inconsistent outputs when source files contain missing keys, duplicate invoices, invalid amounts, late payments, overdue balances, or expired contract logic. The business question is:

> How can recurring operational reporting be automated so that business users receive consistent, validated, and dashboard-ready outputs with less manual effort and fewer reporting errors?

## Solution Overview

The project builds an automated reporting prototype that turns raw synthetic business data into validated reporting tables, KPI summaries, exception logs, audit checks, and a BI-ready output file.

```text
Synthetic raw data
  -> schema and data quality validation
  -> cleaned processed tables
  -> invoice/payment/customer transformations
  -> monthly and customer KPI calculations
  -> business-readable exception report
  -> Power BI-ready dashboard export
  -> Streamlit reporting demo
```

## Dataset Description

The synthetic dataset supports monthly management reporting across customers, invoices, payments, contracts, service cases, and monthly targets.

Raw tables:
- `customers.csv`: customer master data, country, industry, risk rating, account manager, active flag
- `invoices.csv`: invoice dates, due dates, invoice amounts, status
- `payments.csv`: payment dates, payment amounts, payment method
- `contracts.csv`: annual contract value, product line, contract status
- `claims_or_cases.csv`: operational case volume and case amount
- `monthly_targets.csv`: revenue and collection-rate targets by country and product line

## Workflow

Run the complete pipeline from the repository root:

```bash
python src/run_pipeline.py
```

Individual steps:

```bash
python src/generate_synthetic_data.py
python src/validate_data.py
python src/transform_data.py
python src/calculate_kpis.py
python src/generate_reports.py
python src/export_powerbi.py
```

## Data Validation Layer

The validation step writes `output/audit/data_quality_report.csv` with check name, table name, status, records checked, failed records, failure rate, severity, and timestamp.

Implemented checks include required columns, duplicate primary keys, customer/invoice referential integrity, non-negative invoice and payment amounts, due dates after invoice dates, reasonable payment dates, valid status values, valid active flags, and target-rate ranges.

## Exception Reporting Layer

The workflow creates `output/exceptions/reporting_exceptions.csv` with business-readable exceptions, severity, explanation, and suggested action.

Exception types include missing customer data, invoice without payment, overdue invoice, payment after due date, high overdue ratio, negative amount, inactive customer with open invoice, contract expired but invoice active, and duplicate invoice ID.

## KPI Logic

Core metrics include total revenue, collected amount, outstanding amount, overdue amount, collection rate, overdue rate, average days to payment, active customers, high-risk customer share, case volume, open cases, revenue vs target, target achievement rate, month-over-month revenue change, top outstanding customers, and high-risk overdue exposure.

## SQL Analytics Layer

The `sql/` folder shows PostgreSQL-style reporting queries with CTEs, joins, aggregations, `CASE WHEN`, date logic, window functions, and dashboard export logic:

- `01_raw_data_checks.sql`
- `02_reporting_base_table.sql`
- `03_kpi_calculations.sql`
- `04_exception_report.sql`
- `05_dashboard_export.sql`
- `06_monthly_reporting_summary.sql`

## Dashboard Design

The Streamlit demo can be started with:

```bash
streamlit run src/app.py
```

Dashboard pages:
- Executive Overview: revenue, collection rate, outstanding amount, overdue amount, active customers, high-risk overdue exposure
- Monthly Reporting Summary: month-by-month KPIs, revenue vs target, collection rate, overdue rate, open cases
- Customer Reporting: customer drilldown, outstanding amount, overdue ratio, risk rating, account manager, reporting status
- Exception Monitoring: exceptions by severity and type with suggested actions
- Data Quality: audit checks, failed records, failure rate, table-level status

## Repository Structure

```text
config/                 configuration files
data/raw/               synthetic source extracts
data/processed/         cleaned reporting base tables
notebooks/              exploratory notebook
output/reports/         monthly and customer reporting outputs
output/powerbi/         flat BI-ready export
output/audit/           data quality report
output/exceptions/      business exception report
screenshots/            screenshot guidance/placeholders
sql/                    reporting analytics SQL examples
src/                    pipeline and Streamlit application
tests/                  pytest coverage for outputs and logic
```

## Outputs

- `output/reports/monthly_reporting_summary.csv`
- `output/reports/customer_reporting_table.csv`
- `output/exceptions/reporting_exceptions.csv`
- `output/powerbi/powerbi_reporting_dashboard.csv`
- `output/audit/data_quality_report.csv`

## Example Insights

This synthetic portfolio dataset can be used to discuss reporting insights such as overdue exposure by customer, collection-rate trend, high-risk customer share, revenue vs target performance, customers requiring account-manager follow-up, and source-data issues that should be resolved before dashboard publication.

## Skills Demonstrated

| Skill | Where demonstrated |
|---|---|
| Python | Pipeline scripts, data generation, transformations |
| pandas | Cleaning, joins, aggregations, reporting tables |
| SQL | Reporting queries, KPI logic, exception queries |
| Data validation | Schema checks, quality reports, audit outputs |
| Reporting automation | End-to-end pipeline from raw data to reports |
| KPI design | Revenue, collection, overdue, target achievement metrics |
| Exception reporting | Business-readable issue detection |
| Power BI-ready modeling | Flat export table for dashboards |
| Streamlit | Interactive reporting demo |
| Docker | Reproducible environment |
| CI/CD | Automated tests through GitHub Actions |
| pytest | Validation tests and output checks |
| Business analytics | Management reporting and operational insights |

## Docker

```bash
docker build -t reporting-automation-workflow .
docker run -p 8501:8501 reporting-automation-workflow
```

## Limitations

This is a portfolio implementation using a synthetic reporting dataset. It does not connect to real company systems, does not contain confidential data, and does not claim real business impact. The CSV workflow is designed to make the reporting logic easy to inspect.

## Future Improvements

- Add database loading into PostgreSQL
- Add scheduled orchestration with Airflow or GitHub Actions
- Add Excel workbook generation for finance/reporting users
- Add row-level lineage and source-file audit metadata
- Add Power BI `.pbix` screenshots after dashboard build

## GitHub Repo Polish

Suggested GitHub About:

```text
Synthetic reporting automation project using Python, SQL, validation checks, exception reporting, Streamlit, and Power BI-ready outputs.
```

Suggested Topics:

```text
reporting-automation, data-analytics, python, sql, pandas, business-intelligence, streamlit, powerbi, data-validation, portfolio-project, synthetic-data, kpi-dashboard
```

## Disclaimer

This project uses fully synthetic data created for portfolio demonstration purposes. It is designed to demonstrate reporting automation, validation, KPI calculation, exception monitoring, and BI-ready output design. It does not use real company data and does not claim real business impact.
