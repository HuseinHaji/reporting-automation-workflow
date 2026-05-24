-- Monthly KPI calculations for management reporting.

WITH base AS (
    SELECT *
    FROM reporting.reporting_base_table
),
monthly AS (
    SELECT
        reporting_month,
        COUNT(DISTINCT customer_id) AS total_customers,
        SUM(invoice_amount) AS total_revenue,
        SUM(collected_amount) AS collected_amount,
        SUM(outstanding_amount) AS outstanding_amount,
        SUM(overdue_amount) AS overdue_amount,
        AVG(
            CASE
                WHEN latest_payment_date IS NOT NULL
                THEN latest_payment_date - (reporting_month::date)
            END
        ) AS avg_days_to_payment,
        COUNT(DISTINCT customer_id) FILTER (WHERE risk_rating = 'High') AS high_risk_customers
    FROM base
    GROUP BY reporting_month
),
targets AS (
    SELECT
        DATE_TRUNC('month', month)::date AS reporting_month,
        SUM(target_revenue) AS target_revenue,
        AVG(target_collection_rate) AS target_collection_rate
    FROM raw.monthly_targets
    GROUP BY DATE_TRUNC('month', month)::date
)
SELECT
    m.reporting_month,
    m.total_customers,
    m.total_revenue,
    m.collected_amount,
    m.outstanding_amount,
    m.overdue_amount,
    ROUND(m.collected_amount / NULLIF(m.total_revenue, 0), 4) AS collection_rate,
    ROUND(m.overdue_amount / NULLIF(m.total_revenue, 0), 4) AS overdue_rate,
    ROUND(m.high_risk_customers::numeric / NULLIF(m.total_customers, 0), 4) AS high_risk_customer_share,
    t.target_revenue,
    ROUND(m.total_revenue / NULLIF(t.target_revenue, 0), 4) AS target_achievement_rate,
    ROUND(
        (m.total_revenue - LAG(m.total_revenue) OVER (ORDER BY m.reporting_month))
        / NULLIF(LAG(m.total_revenue) OVER (ORDER BY m.reporting_month), 0),
        4
    ) AS month_over_month_revenue_change
FROM monthly m
LEFT JOIN targets t
    ON m.reporting_month = t.reporting_month
ORDER BY m.reporting_month;
