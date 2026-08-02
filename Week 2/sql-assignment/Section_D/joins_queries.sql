-- Section D: SQL Joins Queries

-- 1. Inner Join: Orders combined with customer profile data
SELECT 
    o.order_id,
    o.order_date,
    c.customer_name,
    c.segment,
    c.region
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;

-- 2. Inner Join: Comprehensive line item analysis combining four tables
SELECT 
    oi.item_id,
    o.order_id,
    o.order_date,
    c.customer_name,
    p.product_name,
    p.category,
    oi.sales,
    oi.quantity,
    oi.profit
FROM order_items oi
INNER JOIN orders o ON oi.order_id = o.order_id
INNER JOIN customers c ON o.customer_id = c.customer_id
INNER JOIN products p ON oi.product_id = p.product_id;

-- 3. Left Join: All customers with their associated order history
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    o.order_id,
    o.order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- 4. Left Join: Identify products that have not been purchased yet
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    oi.item_id
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.item_id IS NULL;

-- 5. Multi-Table Join & Aggregation: Segment performance breakdown
SELECT 
    c.segment,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.sales) AS segment_revenue,
    SUM(oi.profit) AS segment_profit
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.segment
ORDER BY segment_revenue DESC;
