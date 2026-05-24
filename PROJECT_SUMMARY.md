# Project Summary

## Problem

Recurring monthly reporting often depends on manual extracts, spreadsheet checks, KPI calculations, and dashboard preparation. In a realistic analyst workflow, source data can contain duplicate invoices, missing customer references, overdue balances, invalid amounts, and inconsistent status values.

## Solution

This project implements an automated reporting prototype using a synthetic reporting dataset. The pipeline generates raw business data, validates source quality, creates cleaned reporting tables, calculates KPIs, detects business exceptions, and exports dashboard-ready files.

## Workflow

1. Generate synthetic customer, invoice, payment, contract, case, and target data.
2. Validate required columns, keys, dates, amounts, statuses, and relationships.
3. Transform raw extracts into clean reporting base tables.
4. Calculate monthly and customer-level KPIs.
5. Produce business-readable exception reports.
6. Export a Power BI-ready flat dashboard table.
7. Present the outputs in an optional Streamlit reporting demo.

## Business Value

- Reduces repetitive manual reporting steps in a simulated workflow.
- Creates consistent KPI definitions for monthly management reporting.
- Detects reporting exceptions before dashboard publication.
- Produces clean BI-ready output tables.
- Demonstrates analyst workflow from raw data to management reporting.

## Technical Skills Demonstrated

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

## Outputs

- Monthly KPI summary: `output/reports/monthly_reporting_summary.csv`
- Customer reporting table: `output/reports/customer_reporting_table.csv`
- Exception report: `output/exceptions/reporting_exceptions.csv`
- Data quality audit: `output/audit/data_quality_report.csv`
- Dashboard export: `output/powerbi/powerbi_reporting_dashboard.csv`

## How This Maps To Real Analyst Work

The project mirrors common BI and reporting analyst responsibilities: checking source extracts, reconciling customer and invoice data, applying business rules, calculating management KPIs, explaining exceptions, preparing dashboard-ready tables, and documenting limitations. It is designed to be credible for Data Analyst, BI Analyst, Reporting Analyst, Junior Analytics Engineer, Business Analyst, and financial services or insurance analytics applications in Germany.
