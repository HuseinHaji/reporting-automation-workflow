-- Raw data quality checks for the synthetic monthly reporting workflow.
-- PostgreSQL-style syntax with Oracle-style business reporting controls.

WITH invoice_checks AS (
    SELECT
        'invoices' AS table_name,
        COUNT(*) AS records_checked,
        COUNT(*) FILTER (WHERE invoice_id IS NULL OR customer_id IS NULL) AS missing_key_records,
        COUNT(*) FILTER (WHERE invoice_amount < 0) AS negative_amount_records,
        COUNT(*) FILTER (WHERE due_date < invoice_date) AS invalid_due_date_records
    FROM raw.invoices
),
duplicate_invoices AS (
    SELECT
        invoice_id,
        COUNT(*) AS duplicate_count
    FROM raw.invoices
    GROUP BY invoice_id
    HAVING COUNT(*) > 1
),
orphan_invoices AS (
    SELECT COUNT(*) AS orphan_invoice_records
    FROM raw.invoices i
    LEFT JOIN raw.customers c
        ON i.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
)
SELECT
    ic.table_name,
    ic.records_checked,
    ic.missing_key_records,
    ic.negative_amount_records,
    ic.invalid_due_date_records,
    COALESCE(SUM(di.duplicate_count), 0) AS duplicate_invoice_records,
    oi.orphan_invoice_records
FROM invoice_checks ic
CROSS JOIN orphan_invoices oi
LEFT JOIN duplicate_invoices di
    ON TRUE
GROUP BY
    ic.table_name,
    ic.records_checked,
    ic.missing_key_records,
    ic.negative_amount_records,
    ic.invalid_due_date_records,
    oi.orphan_invoice_records;
