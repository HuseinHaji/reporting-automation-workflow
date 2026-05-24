"""Streamlit demo for the synthetic reporting automation workflow."""

from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "output" / "reports"
AUDIT = ROOT / "output" / "audit"
EXCEPTIONS = ROOT / "output" / "exceptions"
POWERBI = ROOT / "output" / "powerbi"


@st.cache_data
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    st.metric(label=label, value=value, delta=delta)


def require_outputs() -> bool:
    required = [
        REPORTS / "monthly_reporting_summary.csv",
        REPORTS / "customer_reporting_table.csv",
        EXCEPTIONS / "reporting_exceptions.csv",
        AUDIT / "data_quality_report.csv",
        POWERBI / "powerbi_reporting_dashboard.csv",
    ]
    missing = [path for path in required if not path.exists()]
    if missing:
        st.error("Reporting outputs are missing. Run `python src/run_pipeline.py` from the repository root.")
        st.write([str(path.relative_to(ROOT)) for path in missing])
        return False
    return True


def main() -> None:
    st.set_page_config(page_title="Reporting Automation Workflow", layout="wide")
    st.title("Reporting Automation Workflow")
    st.caption("Synthetic reporting dataset | monthly management reporting | exception monitoring | BI-ready export")

    if not require_outputs():
        return

    monthly = load_csv(REPORTS / "monthly_reporting_summary.csv")
    customers = load_csv(REPORTS / "customer_reporting_table.csv")
    exceptions = load_csv(EXCEPTIONS / "reporting_exceptions.csv")
    quality = load_csv(AUDIT / "data_quality_report.csv")
    powerbi = load_csv(POWERBI / "powerbi_reporting_dashboard.csv")

    months = sorted(monthly["reporting_month"].unique())
    countries = sorted(customers["country"].unique())
    industries = sorted(customers["industry"].unique())
    risks = sorted(customers["risk_rating"].unique())

    with st.sidebar:
        st.header("Filters")
        selected_month = st.selectbox("Reporting month", months, index=len(months) - 1)
        selected_country = st.multiselect("Country", countries, default=countries)
        selected_industry = st.multiselect("Industry", industries, default=industries)
        selected_risk = st.multiselect("Risk rating", risks, default=risks)

    filtered_customers = customers[
        customers["country"].isin(selected_country)
        & customers["industry"].isin(selected_industry)
        & customers["risk_rating"].isin(selected_risk)
    ].copy()
    current = monthly[monthly["reporting_month"] == selected_month].iloc[0]

    tabs = st.tabs(
        [
            "Executive Overview",
            "Monthly Reporting Summary",
            "Customer Reporting Table",
            "Exception Report",
            "Data Quality",
            "Revenue vs Target",
            "Methodology",
        ]
    )

    with tabs[0]:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total revenue", f"EUR {current['total_revenue']:,.0f}")
        col2.metric("Collection rate", f"{current['collection_rate']:.1%}")
        col3.metric("Outstanding", f"EUR {current['outstanding_amount']:,.0f}")
        col4.metric("Overdue", f"EUR {current['overdue_amount']:,.0f}")
        col5.metric("Active customers", f"{int(current['active_customers']):,}")
        high_risk_exposure = filtered_customers.loc[filtered_customers["risk_rating"] == "High", "overdue_amount"].sum()
        col6.metric("High-risk overdue", f"EUR {high_risk_exposure:,.0f}")

        left, right = st.columns(2)
        left.subheader("Revenue trend")
        left.line_chart(monthly.set_index("reporting_month")[["total_revenue", "collected_amount"]])
        right.subheader("Exception severity overview")
        right.bar_chart(exceptions["severity"].value_counts())

    with tabs[1]:
        st.subheader("Month-by-month KPIs")
        st.dataframe(monthly, use_container_width=True, hide_index=True)
        st.line_chart(monthly.set_index("reporting_month")[["collection_rate", "overdue_rate", "target_achievement_rate"]])
        st.line_chart(monthly.set_index("reporting_month")[["open_cases"]])

    with tabs[2]:
        st.subheader("Customer drilldown")
        st.dataframe(
            filtered_customers.sort_values("outstanding_amount", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
        st.bar_chart(filtered_customers.set_index("customer_name")["outstanding_amount"].sort_values(ascending=False).head(15))

    with tabs[3]:
        st.subheader("Business-readable reporting exceptions")
        st.dataframe(exceptions, use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        col1.bar_chart(exceptions["exception_type"].value_counts().head(10))
        col2.bar_chart(exceptions["severity"].value_counts())

    with tabs[4]:
        st.subheader("Validation and audit checks")
        st.dataframe(quality, use_container_width=True, hide_index=True)
        st.bar_chart(quality.set_index("check_name")["failed_records"])

    with tabs[5]:
        st.subheader("Revenue vs target")
        target_view = monthly[["reporting_month", "total_revenue", "target_revenue", "target_achievement_rate", "mom_revenue_change"]]
        st.dataframe(target_view, use_container_width=True, hide_index=True)
        st.line_chart(target_view.set_index("reporting_month")[["total_revenue", "target_revenue"]])

    with tabs[6]:
        st.subheader("Workflow design")
        st.write(
            "This portfolio implementation uses a synthetic reporting dataset to demonstrate an automated monthly "
            "management reporting workflow: raw files, validation checks, transformation, KPI calculation, exception "
            "monitoring, dashboard-ready export, and audit output."
        )
        st.dataframe(powerbi.head(20), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
