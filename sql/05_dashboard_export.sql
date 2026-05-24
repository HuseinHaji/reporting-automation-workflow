-- Flat dashboard export base query for Power BI or Streamlit.

WITH customer_reporting AS (
    SELECT
        customer_id,
        customer_name,
        country,
        industry,
        company_size,
        risk_rating,
        account_manager,
        SUM(invoice_amount) AS total_invoice_amount,
        SUM(collected_amount) AS collected_amount,
        SUM(outstanding_amount) AS outstanding_amount,
        SUM(overdue_amount) AS overdue_amount,
        SUM(overdue_amount) / NULLIF(SUM(invoice_amount), 0) AS overdue_ratio,
        CASE
            WHEN SUM(overdue_amount) / NULLIF(SUM(invoice_amount), 0) > 0.30 THEN 'High Overdue'
            WHEN SUM(outstanding_amount) > 0 THEN 'Outstanding'
            ELSE 'Ready'
        END AS reporting_status
    FROM reporting.reporting_base_table
    GROUP BY
        customer_id,
        customer_name,
        country,
        industry,
        company_size,
        risk_rating,
        account_manager
),
latest_month AS (
    SELECT *
    FROM reporting.monthly_reporting_summary
    ORDER BY reporting_month DESC
    LIMIT 1
)
SELECT
    lm.reporting_month,
    cr.*,
    CASE
        WHEN cr.risk_rating = 'High' THEN 'High Risk'
        WHEN cr.risk_rating = 'Medium' THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_category,
    lm.total_revenue,
    lm.collection_rate,
    lm.overdue_rate,
    lm.target_revenue,
    lm.target_achievement_rate
FROM customer_reporting cr
CROSS JOIN latest_month lm
ORDER BY cr.outstanding_amount DESC;
