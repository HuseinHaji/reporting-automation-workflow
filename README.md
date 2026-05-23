# Reporting Automation Workflow

End-to-end reporting automation project that validates recurring business inputs, calculates plan-versus-actual performance, separates data-quality issues, and creates a controlled reporting pack.

## Business Goal

Monthly reporting often fails because manual spreadsheets mix calculations, ownership gaps, and quality issues in one place. This workflow separates those concerns into a repeatable control process: validate, calculate, route issues, and publish clean reporting outputs.

## Architecture

```mermaid
flowchart LR
    A[Monthly Input CSV] --> B[Schema + Quality Checks]
    B --> C[Variance Engine]
    C --> D[Monthly Report]
    B --> E[Quality Issue Register]
    C --> F[Business Unit Scorecard]
    D --> G[Management Pack]
    E --> H[Owner Follow-up]
```

## Repository Structure

```text
.
├── data/
│   └── monthly_input.csv
├── output/
│   ├── business_unit_scorecard.csv
│   ├── control_summary.csv
│   ├── monthly_report.csv
│   └── quality_issues.csv
└── src/
    └── run_report.py
```

## What The Pipeline Does

- Validates required reporting fields and flags missing owners, zero actuals, and zero plans.
- Calculates variance in euros and percentage against plan.
- Adds status and action fields so review items can be routed.
- Builds a business-unit scorecard for management review.
- Creates a control summary showing row count, variance, issue count, and report readiness.

## Outputs

| File | Purpose |
| --- | --- |
| `output/monthly_report.csv` | Clean report rows with variance, status, and action fields. |
| `output/quality_issues.csv` | Issue register with severity and business-unit context. |
| `output/business_unit_scorecard.csv` | Aggregated plan-versus-actual performance by unit. |
| `output/control_summary.csv` | One-row control dashboard for report readiness. |

## Run Locally

```bash
python3 src/run_report.py
```

No third-party packages are required; the project uses the Python standard library.

## Skills Demonstrated

Reporting automation, data-quality controls, variance analysis, workflow design, exception handling, and management-ready output design.
