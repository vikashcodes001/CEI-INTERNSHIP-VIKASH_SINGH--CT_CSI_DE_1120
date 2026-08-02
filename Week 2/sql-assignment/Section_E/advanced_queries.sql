-- Section E: Advanced Queries (CASE Statements, CTEs, Window Functions, Transactions)

-- 1. Categorize order items by sales tier using CASE statement
SELECT 
    item_id,
    order_id,
    sales,
    CASE 
        WHEN sales >= 500 THEN 'High Value'
        WHEN sales BETWEEN 100 AND 499.99 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS order_tier
FROM order_items;

-- 2. Evaluate item profitability status using CASE statement
SELECT 
    item_id,
    order_id,
    profit,
    CASE 
        WHEN profit > 0 THEN 'Profitable'
        WHEN profit = 0 THEN 'Breakeven'
        ELSE 'Loss'
    END AS profit_status
FROM order_items;

-- 3. Subquery: Retrieve order items performing above average sales
SELECT 
    item_id,
    order_id,
    product_id,
    sales
FROM order_items
WHERE sales > (SELECT AVG(sales) FROM order_items);

-- 4. CTE & Window Functions: Rank customers by cumulative sales revenue
WITH CustomerTotals AS (
    SELECT 
        o.customer_id,
        SUM(oi.sales) AS total_spent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.customer_id
)
SELECT 
    c.customer_name,
    ct.total_spent,
    DENSE_RANK() OVER (ORDER BY ct.total_spent DESC) AS spend_rank,
    ROW_NUMBER() OVER (ORDER BY ct.total_spent DESC) AS row_num
FROM CustomerTotals ct
JOIN customers c ON ct.customer_id = c.customer_id;

-- 5. CTE & Subquery: Filter high-tier customers spending above customer average
WITH CustomerSpend AS (
    SELECT 
        customer_id,
        SUM(sales) AS total_sales
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY customer_id
)
SELECT 
    c.customer_name,
    cs.total_sales
FROM CustomerSpend cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_sales > (SELECT AVG(total_sales) FROM CustomerSpend);

-- 6. Transaction management: Atomic insertion of order and order line item
BEGIN TRANSACTION;

INSERT INTO orders (order_id, customer_id, order_date, ship_date, ship_mode)
VALUES ('CA-2023-999999', 'CG-12520', '2023-10-01', '2023-10-05', 'Standard Class');

INSERT INTO order_items (item_id, order_id, product_id, sales, quantity, discount, profit)
VALUES (6, 'CA-2023-999999', 'OFF-ST-10000760', 150.00, 3, 0.00, 35.00);

COMMIT;
