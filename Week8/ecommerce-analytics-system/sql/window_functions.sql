-- Customer Lifetime Value ranking
WITH customer_spend AS (
    SELECT 
        c.customer_id,
        c.name,
        c.segment,
        COUNT(DISTINCT o.order_id) AS total_orders,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS lifetime_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.name, c.segment
)
SELECT 
    customer_id,
    name,
    segment,
    total_orders,
    lifetime_value,
    DENSE_RANK() OVER (ORDER BY lifetime_value DESC) AS ltv_rank
FROM customer_spend
ORDER BY ltv_rank ASC
LIMIT 15;

-- Daily sales running totals & 7-day moving average
WITH daily_revenue AS (
    SELECT 
        o.order_date,
        COUNT(DISTINCT o.order_id) AS daily_orders,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS daily_sales
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.order_date
)
SELECT 
    order_date,
    daily_orders,
    daily_sales,
    ROUND(SUM(daily_sales) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_revenue,
    ROUND(AVG(daily_sales) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS moving_avg_7d
FROM daily_revenue
ORDER BY order_date ASC;

-- Month-over-Month (MoM) growth rate
WITH monthly_sales AS (
    SELECT 
        strftime('%Y-%m', o.order_date) AS rev_month,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY rev_month
),
monthly_lag AS (
    SELECT 
        rev_month,
        total_revenue,
        LAG(total_revenue, 1) OVER (ORDER BY rev_month) AS previous_month_revenue
    FROM monthly_sales
)
SELECT 
    rev_month,
    total_revenue,
    COALESCE(previous_month_revenue, 0) AS prev_month_revenue,
    ROUND(total_revenue - COALESCE(previous_month_revenue, total_revenue), 2) AS mom_change,
    ROUND(
        CASE 
            WHEN previous_month_revenue IS NULL OR previous_month_revenue = 0 THEN 0.0
            ELSE ((total_revenue - previous_month_revenue) / previous_month_revenue) * 100.0
        END, 
        2
    ) AS mom_growth_pct
FROM monthly_lag
ORDER BY rev_month ASC;
