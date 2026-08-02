-- Section C: Aggregation & Grouping Queries

-- 1. Summary metrics across all order line items
SELECT 
    COUNT(item_id) AS total_items_sold,
    SUM(sales) AS grand_total_sales,
    AVG(sales) AS avg_item_sales,
    MIN(sales) AS min_item_sales,
    MAX(sales) AS max_item_sales,
    SUM(profit) AS grand_total_profit
FROM order_items;

-- 2. Customer distribution across market segments
SELECT 
    segment, 
    COUNT(customer_id) AS total_customers
FROM customers
GROUP BY segment
ORDER BY total_customers DESC;

-- 3. Total sales revenue and quantity per order
SELECT 
    order_id,
    SUM(sales) AS total_order_sales,
    SUM(quantity) AS total_items,
    AVG(discount) AS avg_discount
FROM order_items
GROUP BY order_id;

-- 4. Product distribution across categories and sub-categories
SELECT 
    category,
    sub_category,
    COUNT(product_id) AS product_count
FROM products
GROUP BY category, sub_category
ORDER BY category, product_count DESC;

-- 5. Orders with cumulative sales exceeding 500
SELECT 
    order_id,
    SUM(sales) AS order_total
FROM order_items
GROUP BY order_id
HAVING SUM(sales) > 500.00;

-- 6. Sales performance and profit contribution per product
SELECT 
    product_id,
    COUNT(item_id) AS times_ordered,
    AVG(quantity) AS avg_quantity_per_order,
    SUM(profit) AS total_product_profit
FROM order_items
GROUP BY product_id
ORDER BY total_product_profit DESC;
