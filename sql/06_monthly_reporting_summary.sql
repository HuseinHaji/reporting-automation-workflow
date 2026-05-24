-- Monthly reporting summary with operational analytics.

WITH base AS (
    SELECT *
    FROM reporting.reporting_base_table
),
case_summary AS (
    SELECT
        DATE_TRUNC('month', case_date)::date AS reporting_month,
        COUNT(*) FILTER (WHERE case_status IN ('Open', 'In Review')) AS open_cases,
        COUNT(*) FILTER (WHERE case_status = 'Closed') AS closed_cases,
        SUM(case_amount) AS case_amount
    FROM raw.claims_or_cases
    GROUP BY DATE_TRUNC('month', case_date)::date
),
top_outstanding AS (
    SELECT
        customer_id,
        customer_name,
        country,
        industry,
        risk_rating,
        SUM(outstanding_amount) AS outstanding_amount,
        SUM(overdue_amount) AS overdue_amount,
        RANK() OVER (ORDER BY SUM(outstanding_amount) DESC) AS outstanding_rank
    FROM base
    GROUP BY customer_id, customer_name, country, industry, risk_rating
)
SELECT
    k.reporting_month,
    k.total_revenue,
    k.collected_amount,
    k.outstanding_amount,
    k.overdue_amount,
    k.collection_rate,
    k.overdue_rate,
    cs.open_cases,
    cs.closed_cases,
    cs.case_amount,
    SUM(CASE WHEN t.risk_rating = 'High' THEN t.overdue_amount ELSE 0 END) AS high_risk_overdue_exposure,
    COUNT(*) FILTER (WHERE t.outstanding_rank <= 10) AS top_10_outstanding_customers
FROM reporting.monthly_reporting_summary k
LEFT JOIN case_summary cs
    ON k.reporting_month = cs.reporting_month
CROSS JOIN top_outstanding t
GROUP BY
    k.reporting_month,
    k.total_revenue,
    k.collected_amount,
    k.outstanding_amount,
    k.overdue_amount,
    k.collection_rate,
    k.overdue_rate,
    cs.open_cases,
    cs.closed_cases,
    cs.case_amount
ORDER BY k.reporting_month;
