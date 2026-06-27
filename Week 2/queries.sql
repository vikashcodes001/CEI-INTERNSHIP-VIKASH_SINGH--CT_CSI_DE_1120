-- 1. Total number of records in the dataset
SELECT COUNT(*) AS total_records FROM sales;

-- 2. Sample data to inspect row structures
SELECT row_id, order_id, order_date, customer_name, category, sales, profit
FROM sales
LIMIT 5;

-- 3. Number of unique categories, sub-categories, regions, customers, and products
SELECT 
    COUNT(DISTINCT category) AS unique_categories,
    COUNT(DISTINCT sub_category) AS unique_sub_categories,
    COUNT(DISTINCT region) AS unique_regions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS unique_products
FROM sales;

-- 4. Sales performance in the West region
SELECT COUNT(*) AS west_region_count, ROUND(SUM(sales), 2) AS west_region_sales
FROM sales
WHERE region = 'West';

-- 5. Sales and average profit for the Technology category
SELECT COUNT(*) AS tech_count, ROUND(SUM(sales), 2) AS tech_sales, ROUND(AVG(profit), 2) AS tech_avg_profit
FROM sales
WHERE category = 'Technology';

-- 6. Total sales generated during the year 2017
SELECT COUNT(*) AS sales_count_2017, ROUND(SUM(sales), 2) AS total_sales_2017
FROM sales
WHERE order_date BETWEEN '2017-01-01' AND '2017-12-31';

-- 7. High-value sales counts and totals (sales greater than $1000)
SELECT COUNT(*) AS high_value_count, ROUND(SUM(sales), 2) AS high_value_sales_total
FROM sales
WHERE sales > 1000;

-- 8. High-value Technology orders in the West region (sales > $500)
SELECT row_id, order_id, customer_name, sales, profit
FROM sales
WHERE region = 'West' 
  AND category = 'Technology' 
  AND sales > 500
ORDER BY sales DESC;

-- 9. Sales, quantity, profit, and average discount grouped by Category
SELECT 
    category,
    COUNT(*) AS order_line_count,
    SUM(quantity) AS total_quantity_sold,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(discount) * 100, 2) AS avg_discount_percentage
FROM sales
GROUP BY category
ORDER BY total_sales DESC;

-- 10. Sales and profit margin grouped by Region
SELECT 
    region,
    COUNT(*) AS order_line_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100, 2) AS profit_margin_percentage
FROM sales
GROUP BY region
ORDER BY total_sales DESC;

-- 11. Sales, profit, and quantity sold by Sub-Category
SELECT 
    category,
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    SUM(quantity) AS total_quantity_sold
FROM sales
GROUP BY category, sub_category
ORDER BY category ASC, total_sales DESC;

-- 12. Top 10 products based on total sales
SELECT 
    product_id,
    product_name,
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    SUM(quantity) AS total_quantity
FROM sales
GROUP BY product_id, product_name, category
ORDER BY total_sales DESC
LIMIT 10;

-- 13. Top 5 sub-categories by total profit
SELECT 
    sub_category,
    category,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales
GROUP BY sub_category, category
ORDER BY total_profit DESC
LIMIT 5;

-- 14. Bottom 5 loss-making sub-categories
SELECT 
    sub_category,
    category,
    ROUND(SUM(profit), 2) AS total_profit
FROM sales
GROUP BY sub_category, category
ORDER BY total_profit ASC
LIMIT 5;

-- 15. Monthly sales and profit trends
SELECT 
    strftime('%Y-%m', order_date) AS order_month,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS unique_orders
FROM sales
GROUP BY order_month
ORDER BY order_month ASC;

-- 16. Top 10 customers based on total spend
SELECT 
    customer_id,
    customer_name,
    segment,
    ROUND(SUM(sales), 2) AS total_spend,
    ROUND(SUM(profit), 2) AS total_profit,
    COUNT(DISTINCT order_id) AS total_orders
FROM sales
GROUP BY customer_id, customer_name, segment
ORDER BY total_spend DESC
LIMIT 10;

-- 17. Find duplicate transactions
SELECT 
    order_id,
    product_id,
    COUNT(*) AS line_occurrences,
    SUM(quantity) AS total_qty_for_product
FROM sales
GROUP BY order_id, product_id
HAVING COUNT(*) > 1
ORDER BY line_occurrences DESC
LIMIT 10;

-- 18.Check for null or empty values in critical columns
SELECT 
    SUM(CASE WHEN row_id IS NULL THEN 1 ELSE 0 END) AS null_row_ids,
    SUM(CASE WHEN order_id IS NULL OR order_id = '' THEN 1 ELSE 0 END) AS empty_order_ids,
    SUM(CASE WHEN order_date IS NULL OR order_date = '' THEN 1 ELSE 0 END) AS empty_order_dates,
    SUM(CASE WHEN customer_id IS NULL OR customer_id = '' THEN 1 ELSE 0 END) AS empty_customer_ids,
    SUM(CASE WHEN product_id IS NULL OR product_id = '' THEN 1 ELSE 0 END) AS empty_product_ids,
    SUM(CASE WHEN sales IS NULL THEN 1 ELSE 0 END) AS null_sales,
    SUM(CASE WHEN profit IS NULL THEN 1 ELSE 0 END) AS null_profits
FROM sales;

-- 19.Check for invalid sales or quantity values (values <= 0)
SELECT 
    SUM(CASE WHEN sales <= 0 THEN 1 ELSE 0 END) AS zero_or_negative_sales,
    SUM(CASE WHEN quantity <= 0 THEN 1 ELSE 0 END) AS zero_or_negative_quantity
FROM sales;
