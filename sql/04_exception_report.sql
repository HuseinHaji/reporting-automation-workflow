-- Business-readable exception reporting logic.

WITH invoice_payment_status AS (
    SELECT
        b.*,
        CASE WHEN b.collected_amount = 0 THEN 1 ELSE 0 END AS invoice_without_payment,
        CASE WHEN b.overdue_amount > 0 THEN 1 ELSE 0 END AS overdue_invoice,
        CASE WHEN b.latest_payment_date > b.due_date THEN 1 ELSE 0 END AS paid_after_due_date
    FROM reporting.reporting_base_table b
),
customer_overdue AS (
    SELECT
        customer_id,
        SUM(invoice_amount) AS total_invoice_amount,
        SUM(overdue_amount) AS overdue_amount,
        SUM(overdue_amount) / NULLIF(SUM(invoice_amount), 0) AS overdue_ratio
    FROM invoice_payment_status
    GROUP BY customer_id
),
exceptions AS (
    SELECT
        reporting_month,
        customer_id,
        'Invoice without payment' AS exception_type,
        'Medium' AS severity,
        'Invoice has no matching payment record.' AS description,
        'Review collection status and expected payment timing.' AS suggested_action
    FROM invoice_payment_status
    WHERE invoice_without_payment = 1

    UNION ALL

    SELECT
        reporting_month,
        customer_id,
        'Overdue invoice',
        'High',
        'Invoice has outstanding value past the due date.',
        'Follow up with account manager and review payment behavior.'
    FROM invoice_payment_status
    WHERE overdue_invoice = 1

    UNION ALL

    SELECT
        DATE_TRUNC('month', CURRENT_DATE)::date,
        customer_id,
        'High overdue ratio',
        'High',
        'Customer overdue amount is above 30% of invoiced amount.',
        'Review customer payment behavior and collections priority.'
    FROM customer_overdue
    WHERE overdue_ratio > 0.30
)
SELECT
    ROW_NUMBER() OVER (ORDER BY severity DESC, customer_id) AS exception_id,
    *
FROM exceptions;
