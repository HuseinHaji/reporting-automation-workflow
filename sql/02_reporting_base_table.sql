-- Customer and invoice reporting base table.

WITH payment_summary AS (
    SELECT
        invoice_id,
        MAX(payment_date) AS latest_payment_date,
        SUM(payment_amount) AS collected_amount
    FROM raw.payments
    WHERE payment_amount >= 0
    GROUP BY invoice_id
),
clean_invoices AS (
    SELECT
        i.invoice_id,
        i.customer_id,
        i.invoice_date,
        i.due_date,
        i.invoice_amount,
        i.status,
        DATE_TRUNC('month', i.invoice_date)::date AS reporting_month
    FROM raw.invoices i
    INNER JOIN raw.customers c
        ON i.customer_id = c.customer_id
    WHERE i.invoice_amount >= 0
      AND i.due_date >= i.invoice_date
),
base AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.country,
        c.industry,
        c.company_size,
        c.risk_rating,
        c.account_manager,
        ci.invoice_id,
        ci.reporting_month,
        ci.invoice_amount,
        COALESCE(ps.collected_amount, 0) AS collected_amount,
        GREATEST(ci.invoice_amount - COALESCE(ps.collected_amount, 0), 0) AS outstanding_amount,
        CASE
            WHEN COALESCE(ps.collected_amount, 0) < ci.invoice_amount
             AND ci.due_date < CURRENT_DATE
            THEN GREATEST(ci.invoice_amount - COALESCE(ps.collected_amount, 0), 0)
            ELSE 0
        END AS overdue_amount,
        ps.latest_payment_date,
        ci.due_date
    FROM clean_invoices ci
    INNER JOIN raw.customers c
        ON ci.customer_id = c.customer_id
    LEFT JOIN payment_summary ps
        ON ci.invoice_id = ps.invoice_id
)
SELECT *
FROM base;
