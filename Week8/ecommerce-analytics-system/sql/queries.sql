-- 1. Total revenue per category
SELECT 
    p.category,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 2. Top 10 customers by total order value
SELECT 
    c.customer_id,
    c.name,
    c.segment,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.customer_id, c.name, c.segment
ORDER BY total_order_value DESC
LIMIT 10;

-- 3. Month-wise order count for the last 12 months
SELECT 
    strftime('%Y-%m', o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(DISTINCT o.customer_id) AS active_customers,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monthly_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date >= date('now', '-12 months')
GROUP BY month
ORDER BY month ASC;

-- 4. Find customers who placed orders but never had any item delivered
SELECT 
    c.customer_id,
    c.name,
    c.email,
    COUNT(o.order_id) AS non_delivered_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_status = 'Completed'
)
GROUP BY c.customer_id, c.name, c.email;

-- 5. Products that were ordered but had more returns than purchases
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(CASE WHEN o.order_status = 'Returned' THEN oi.quantity ELSE 0 END) AS returned_qty,
    SUM(CASE WHEN o.order_status = 'Completed' THEN oi.quantity ELSE 0 END) AS purchased_qty
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.product_id, p.product_name, p.category
HAVING returned_qty > purchased_qty;

-- 6. Calculate the return rate per category
SELECT 
    p.category,
    SUM(CASE WHEN o.order_status = 'Returned' THEN oi.quantity ELSE 0 END) AS returned_items,
    SUM(oi.quantity) AS total_items,
    ROUND(
        CAST(SUM(CASE WHEN o.order_status = 'Returned' THEN oi.quantity ELSE 0 END) AS REAL) / 
        NULLIF(SUM(oi.quantity), 0) * 100.0, 
        2
    ) AS return_rate_percent
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY p.category
ORDER BY return_rate_percent DESC;

-- 7. Running totals of revenue per date
WITH daily_revenue AS (
    SELECT 
        o.order_date,
        COUNT(DISTINCT o.order_id) AS daily_orders,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY o.order_date
)
SELECT 
    order_date,
    daily_orders,
    daily_revenue,
    ROUND(SUM(daily_revenue) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total
FROM daily_revenue
ORDER BY order_date ASC;

-- 8. Rank products by total revenue per category using DENSE_RANK
WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_id,
        p.product_name,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY p.category, p.product_id, p.product_name
)
SELECT 
    category,
    product_name,
    total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_in_category
FROM product_revenue
ORDER BY category, rank_in_category;

-- 9. Days between consecutive orders per customer & risk status
WITH customer_orders AS (
    SELECT 
        customer_id,
        order_id,
        order_date,
        LAG(order_date, 1) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date
    FROM orders
    WHERE order_status = 'Completed'
),
order_gaps AS (
    SELECT 
        customer_id,
        order_id,
        order_date,
        previous_order_date,
        JULIANDAY(order_date) - JULIANDAY(previous_order_date) AS days_gap
    FROM customer_orders
)
SELECT 
    customer_id,
    ROUND(AVG(days_gap), 1) AS avg_days_gap,
    CASE 
        WHEN AVG(days_gap) > 30 THEN 'At Risk'
        ELSE 'Active / Regular'
    END AS customer_risk_status
FROM order_gaps
WHERE days_gap IS NOT NULL
GROUP BY customer_id;

-- 10. Multi-level CTE: Monthly customer spend tiers
WITH monthly_customer_spend AS (
    SELECT 
        strftime('%Y-%m', o.order_date) AS month,
        o.customer_id,
        SUM(oi.quantity * oi.unit_price) AS monthly_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY month, o.customer_id
),
spend_tiers AS (
    SELECT 
        month,
        customer_id,
        monthly_revenue,
        CASE 
            WHEN monthly_revenue > 10000 THEN 'High'
            WHEN monthly_revenue BETWEEN 5000 AND 10000 THEN 'Medium'
            ELSE 'Low'
        END AS spend_tier
    FROM monthly_customer_spend
)
SELECT 
    month,
    spend_tier,
    COUNT(customer_id) AS customer_count,
    ROUND(SUM(monthly_revenue), 2) AS tier_revenue
FROM spend_tiers
GROUP BY month, spend_tier
ORDER BY month ASC, spend_tier ASC;

-- 11. Customer LTV quartiles (NTILE)
WITH customer_ltv AS (
    SELECT 
        c.customer_id,
        c.name,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, c.name
),
quartiles AS (
    SELECT 
        customer_id,
        name,
        total_value,
        NTILE(4) OVER (ORDER BY total_value DESC) AS quartile
    FROM customer_ltv
)
SELECT 
    customer_id,
    name,
    total_value,
    quartile,
    CASE quartile
        WHEN 1 THEN 'Platinum'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'
    END AS quartile_label
FROM quartiles
ORDER BY total_value DESC;

-- 12. Year-over-Year revenue comparison
WITH monthly_revenue AS (
    SELECT 
        strftime('%Y', order_date) AS year,
        strftime('%m', order_date) AS month,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY year, month
)
SELECT 
    m1.year,
    m1.month,
    m1.revenue,
    m2.revenue AS prev_year_revenue,
    ROUND(
        CASE 
            WHEN m2.revenue IS NULL OR m2.revenue = 0 THEN NULL
            ELSE ((m1.revenue - m2.revenue) / m2.revenue) * 100.0
        END, 
        2
    ) AS yoy_growth_percent
FROM monthly_revenue m1
LEFT JOIN monthly_revenue m2 
    ON m1.month = m2.month AND CAST(m1.year AS INT) = CAST(m2.year AS INT) + 1
ORDER BY m1.year ASC, m1.month ASC;

-- 13. First vs most recent purchased category
WITH ordered_purchases AS (
    SELECT 
        o.customer_id,
        p.category,
        o.order_date,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date ASC, o.order_id ASC) AS rn_first,
        ROW_NUMBER() OVER (PARTITION BY o.customer_id ORDER BY o.order_date DESC, o.order_id DESC) AS rn_last
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed'
),
first_cats AS (
    SELECT customer_id, category AS first_category FROM ordered_purchases WHERE rn_first = 1
),
last_cats AS (
    SELECT customer_id, category AS last_category FROM ordered_purchases WHERE rn_last = 1
)
SELECT 
    f.customer_id,
    f.first_category,
    l.last_category,
    CASE 
        WHEN f.first_category <> l.last_category THEN 'Yes'
        ELSE 'No'
    END AS category_shift
FROM first_cats f
JOIN last_cats l ON f.customer_id = l.customer_id;

-- 14. Cumulative revenue distribution (top N% customers)
WITH customer_revenue AS (
    SELECT 
        c.customer_id,
        SUM(oi.quantity * oi.unit_price) AS revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id
),
running_revenue AS (
    SELECT 
        customer_id,
        revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue,
        SUM(revenue) OVER () AS total_system_revenue
    FROM customer_revenue
)
SELECT 
    customer_id,
    ROUND(revenue, 2) AS revenue,
    ROUND(cumulative_revenue, 2) AS cumulative_revenue,
    ROUND((cumulative_revenue / total_system_revenue) * 100.0, 2) AS cumulative_percent
FROM running_revenue
ORDER BY revenue DESC;

-- 15. Cohort retention matrix (Months 0-3)
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        strftime('%Y-%m', join_date) AS cohort_month
    FROM customers
),
cohort_orders AS (
    SELECT DISTINCT
        o.customer_id,
        cc.cohort_month,
        (CAST(substr(strftime('%Y-%m', o.order_date), 1, 4) AS INT) - CAST(substr(cc.cohort_month, 1, 4) AS INT)) * 12 +
        (CAST(substr(strftime('%Y-%m', o.order_date), 6, 2) AS INT) - CAST(substr(cc.cohort_month, 6, 2) AS INT)) AS month_number
    FROM orders o
    JOIN customer_cohorts cc ON o.customer_id = cc.customer_id
    WHERE o.order_status = 'Completed'
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_size
    FROM customer_cohorts
    GROUP BY cohort_month
)
SELECT 
    co.cohort_month,
    cs.cohort_size,
    co.month_number,
    COUNT(DISTINCT co.customer_id) AS active_users,
    ROUND(CAST(COUNT(DISTINCT co.customer_id) AS REAL) / cs.cohort_size * 100.0, 2) AS retention_rate
FROM cohort_orders co
JOIN cohort_sizes cs ON co.cohort_month = cs.cohort_month
WHERE co.month_number BETWEEN 0 AND 3
GROUP BY co.cohort_month, cs.cohort_size, co.month_number
ORDER BY co.cohort_month, co.month_number;

-- 16. Products frequently bought together (Market Basket Analysis)
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(*) AS times_bought_together
FROM order_items oi1
JOIN order_items oi2 
    ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
JOIN orders o ON oi1.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p1.product_name, p2.product_name
ORDER BY times_bought_together DESC
LIMIT 10;
