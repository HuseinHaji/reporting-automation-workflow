# Reporting Automation Workflow

## Business Context

This project demonstrates an automated reporting workflow for recurring monthly extracts. The business team receives data from multiple systems and needs a standardised process to validate, clean, and deliver report-ready files.

The automation improves consistency and reduces manual effort in recurring reporting tasks.

## Business Value

- Eliminates manual checks for schema and quality issues.
- Enables repeatable monthly reporting with fewer rework cycles.
- Produces clean reporting tables and executive summaries.
- Supports stakeholder confidence through validation metrics.

## Tech Stack

- Python 3.10+ (pandas, numpy, pyyaml)
- Oracle-style SQL examples
- CSV-based file workflow

## Dataset

The dataset is synthetic and represents recurring extracts for customers, transactions, and segment assignments. It includes intentionally introduced validation issues such as missing values, negative amounts, duplicate transaction IDs, and out-of-range dates.

## Workflow

- `generate_raw_data.py`: create synthetic raw extracts.
- `validate_data.py`: enforce schema, missing values, duplicates, negative amounts, and date range rules.
- `transform_data.py`: clean records for reporting.
- `create_report.py`: aggregate reporting metrics.
- `run_pipeline.py`: execute the end-to-end workflow.

## Key KPIs

- Total reportable amount
- Number of records processed
- Validation error count
- Duplicate records detected
- Missing values detected
- Rejected records
- Clean records
- Segment processing summary
- Monthly business unit trend

## Project Structure

```text
reporting-automation-workflow/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   └── reporting_config.yaml
├── data/
│   ├── raw/
│   ├── processed/
│   └── reporting/
├── logs/
│   └── .gitkeep
├── reports/
│   └── .gitkeep
├── sql/
│   └── oracle_style_reporting_queries.sql
├── src/
│   ├── generate_raw_data.py
│   ├── validate_data.py
│   ├── transform_data.py
│   ├── create_report.py
│   └── run_pipeline.py
└── screenshots/
    └── .gitkeep
```

## How to Run

```bash
cd reporting-automation-workflow
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py
```

For Windows:

```powershell
.venv\Scripts\activate
```

## Enhanced portfolio version

- Added a **Streamlit demo** at `src/app.py`.
- Added **Dockerfile** and **docker-compose.yml** for reproducible deployment.
- Added **CI workflows** for linting, testing, and smoke testing.
- Added **sample data**, **unit tests**, and **project notes**.
- Added `PROJECT_SUMMARY.md` and `PROJECT_NOTES.md` for project context.

## Demo

Run the demo with:

```bash
streamlit run src/app.py
```

Or with Docker:

```bash
docker-compose up --build
```

## Dashboard Design

Power BI setup is optional. Load the clean reporting outputs from `data/reporting/` and build pages for Monthly Summary, Segment Performance, Exception Tracking and Trend Analysis.

## Example Insights

- Segment A outperforms in reportable amount while Segment C shows elevated validation errors.
- Duplicate and invalid transactions are concentrated in one business unit, suggesting process improvement.
- Clean records exceed 95% after validation and transformation.

## Future Improvements

- Add data lineage and audit logging.
- Integrate with a scheduling engine for monthly refresh.
- Expand validation rules for business rule exceptions.

## Disclaimer

This project uses fully synthetic data created for portfolio demonstration purposes. It does not contain confidential, proprietary, or real company data.
