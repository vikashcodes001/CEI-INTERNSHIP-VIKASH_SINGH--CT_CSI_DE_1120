-- Cohort monthly retention analysis
WITH first_purchases AS (
    SELECT 
        customer_id,
        MIN(strftime('%Y-%m', order_date)) AS cohort_month
    FROM orders
    WHERE order_status = 'Completed'
    GROUP BY customer_id
),
customer_activities AS (
    SELECT DISTINCT
        o.customer_id,
        fp.cohort_month,
        strftime('%Y-%m', o.order_date) AS activity_month,
        (CAST(substr(strftime('%Y-%m', o.order_date), 1, 4) AS INT) - CAST(substr(fp.cohort_month, 1, 4) AS INT)) * 12 +
        (CAST(substr(strftime('%Y-%m', o.order_date), 6, 2) AS INT) - CAST(substr(fp.cohort_month, 6, 2) AS INT)) AS month_number
    FROM orders o
    JOIN first_purchases fp ON o.customer_id = fp.customer_id
    WHERE o.order_status = 'Completed'
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_customers
    FROM first_purchases
    GROUP BY cohort_month
)
SELECT 
    ca.cohort_month,
    cs.total_cohort_customers,
    ca.month_number,
    COUNT(DISTINCT ca.customer_id) AS active_customers,
    ROUND(CAST(COUNT(DISTINCT ca.customer_id) AS REAL) / cs.total_cohort_customers * 100.0, 2) AS retention_rate_pct
FROM customer_activities ca
JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
GROUP BY ca.cohort_month, cs.total_cohort_customers, ca.month_number
ORDER BY ca.cohort_month ASC, ca.month_number ASC;

-- Churn vs repeat customer classification
WITH customer_order_summary AS (
    SELECT 
        c.customer_id,
        c.name,
        MIN(o.order_date) AS first_order_date,
        MAX(o.order_date) AS last_order_date,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.order_status = 'Completed'
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.name
)
SELECT 
    customer_id,
    name,
    order_count,
    total_spent,
    first_order_date,
    last_order_date,
    CASE 
        WHEN order_count = 0 THEN 'Never Purchased'
        WHEN order_count = 1 THEN 'One-Time / Churned'
        ELSE 'Repeat Customer'
    END AS customer_status
FROM customer_order_summary
ORDER BY total_spent DESC;

-- RFM customer segmentation
WITH customer_rfm_raw AS (
    SELECT 
        c.customer_id,
        c.name,
        c.segment AS raw_segment,
        MAX(o.order_date) AS max_order_date,
        COUNT(DISTINCT o.order_id) AS frequency,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.name, c.segment
),
rfm_scores AS (
    SELECT 
        customer_id,
        name,
        raw_segment,
        frequency,
        monetary,
        max_order_date,
        CASE 
            WHEN frequency = 1 THEN 'One-Time'
            WHEN frequency BETWEEN 2 AND 4 THEN 'Occasional'
            ELSE 'Loyal'
        END AS frequency_tier,
        CASE 
            WHEN monetary < 500 THEN 'Low Spend'
            WHEN monetary BETWEEN 500 AND 2000 THEN 'Medium Spend'
            ELSE 'High Spend'
        END AS spend_tier
    FROM customer_rfm_raw
)
SELECT 
    customer_id,
    name,
    raw_segment,
    frequency,
    monetary,
    frequency_tier,
    spend_tier,
    CASE 
        WHEN frequency_tier = 'Loyal' AND spend_tier = 'High Spend' THEN 'Champions'
        WHEN frequency_tier = 'Loyal' THEN 'Loyal Customers'
        WHEN frequency_tier = 'Occasional' AND spend_tier IN ('Medium Spend', 'High Spend') THEN 'Potential Loyalists'
        WHEN frequency_tier = 'One-Time' AND spend_tier = 'High Spend' THEN 'Big Spenders'
        ELSE 'Recent / Need Nurturing'
    END AS rfm_segment
FROM rfm_scores
ORDER BY monetary DESC;
