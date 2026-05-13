-- Oracle-style reporting queries

-- Total amount by business unit
SELECT business_unit,
       SUM(amount) AS total_amount,
       COUNT(*) AS record_count
FROM clean_reporting_table
GROUP BY business_unit;

-- Monthly trend by business unit
SELECT TO_CHAR(transaction_date, 'YYYY-MM') AS month_key,
       business_unit,
       SUM(amount) AS total_amount
FROM clean_reporting_table
GROUP BY TO_CHAR(transaction_date, 'YYYY-MM'), business_unit
ORDER BY month_key;

-- Validation overview
SELECT status_code,
       COUNT(*) AS count_by_status
FROM rejected_records
GROUP BY status_code;
