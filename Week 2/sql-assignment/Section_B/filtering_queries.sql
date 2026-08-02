-- Section B: Data Filtering Queries

-- 1. Filter orders by shipping mode
SELECT order_id, customer_id, order_date, ship_mode
FROM orders
WHERE ship_mode = 'Second Class';

-- 2. Find high-value line items where sales exceed 500
SELECT item_id, order_id, product_id, sales
FROM order_items
WHERE sales > 500.00
ORDER BY sales DESC;

-- 3. Retrieve customers living in California or Washington
SELECT customer_id, customer_name, state, city
FROM customers
WHERE state IN ('California', 'Washington');

-- 4. Find orders placed within a specific date range
SELECT order_id, customer_id, order_date
FROM orders
WHERE order_date BETWEEN '2016-01-01' AND '2016-12-31';

-- 5. Filter products by category while excluding specific sub-categories
SELECT product_id, product_name, sub_category
FROM products
WHERE category = 'Furniture' AND sub_category != 'Tables';

-- 6. Identify order items with applied discounts
SELECT item_id, order_id, sales, discount, profit
FROM order_items
WHERE discount > 0.00;

-- 7. Search for customers whose names start with 'A'
SELECT customer_id, customer_name, segment
FROM customers
WHERE customer_name LIKE 'A%';

-- 8. Identify unprofitable items with negative profit margins
SELECT item_id, order_id, product_id, sales, profit
FROM order_items
WHERE profit < 0;
