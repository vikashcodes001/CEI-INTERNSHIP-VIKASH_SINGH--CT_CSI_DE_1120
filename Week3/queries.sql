-- ==========================================
-- SQL Script for Superstore Sales Analysis
-- Database: Microsoft SQL Server
-- Internship Week 3 Tasks
-- ==========================================

USE SuperstoreDB;
GO

-- ==========================================
-- STEP 1: SETUP DATA
-- ==========================================

-- 1. Create normalized tables
IF OBJECT_ID('orders', 'U') IS NOT NULL DROP TABLE orders;
IF OBJECT_ID('products', 'U') IS NOT NULL DROP TABLE products;
IF OBJECT_ID('customers', 'U') IS NOT NULL DROP TABLE customers;
GO

-- Create Customers Table
CREATE TABLE customers (
    customer_id NVARCHAR(50) PRIMARY KEY,
    customer_name NVARCHAR(255) NOT NULL,
    segment NVARCHAR(100) NOT NULL
);
GO

-- Create Products Table
CREATE TABLE products (
    product_id NVARCHAR(50) PRIMARY KEY,
    category NVARCHAR(100) NOT NULL,
    sub_category NVARCHAR(100) NOT NULL,
    product_name NVARCHAR(500) NOT NULL
);
GO

-- Create Orders Table
CREATE TABLE orders (
    row_id INT PRIMARY KEY,
    order_id NVARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    ship_mode NVARCHAR(100) NOT NULL,
    customer_id NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES customers(customer_id),
    product_id NVARCHAR(50) NOT NULL FOREIGN KEY REFERENCES products(product_id),
    sales DECIMAL(18, 4) NOT NULL,
    quantity INT NOT NULL,
    discount DECIMAL(18, 4) NOT NULL,
    profit DECIMAL(18, 4) NOT NULL,
    country NVARCHAR(100) NOT NULL,
    city NVARCHAR(100) NOT NULL,
    state NVARCHAR(100) NOT NULL,
    postal_code NVARCHAR(50),
    region NVARCHAR(100) NOT NULL
);
GO

-- 2. Populate normalized tables using SELECT DISTINCT (with deduplication for products)
INSERT INTO customers (customer_id, customer_name, segment)
SELECT DISTINCT 
    [Customer ID], 
    [Customer Name], 
    [Segment]
FROM superstore_raw;
GO

INSERT INTO products (product_id, category, sub_category, product_name)
SELECT 
    [Product ID], 
    [Category], 
    [Sub-Category], 
    MAX([Product Name])
FROM superstore_raw
GROUP BY [Product ID], [Category], [Sub-Category];
GO

INSERT INTO orders (
    row_id, order_id, order_date, ship_date, ship_mode, 
    customer_id, product_id, sales, quantity, discount, profit,
    country, city, state, postal_code, region
)
SELECT 
    CAST([Row ID] AS INT),
    [Order ID],
    CONVERT(DATE, [Order Date], 101),
    CONVERT(DATE, [Ship Date], 101),
    [Ship Mode],
    [Customer ID],
    [Product ID],
    CAST([Sales] AS DECIMAL(18, 4)),
    CAST([Quantity] AS INT),
    CAST([Discount] AS DECIMAL(18, 4)),
    CAST([Profit] AS DECIMAL(18, 4)),
    [Country],
    [City],
    [State],
    [Postal Code],
    [Region]
FROM superstore_raw;
GO

-- ==========================================
-- STEP 2: PERFORM REQUIRED QUERIES
-- ==========================================

-- Query 1: Find all orders where sales are greater than the average sales. (Subquery)
SELECT 
    order_id, 
    sales
FROM orders
WHERE sales > (SELECT AVG(sales) FROM orders)
ORDER BY sales DESC;
GO

-- Query 2: Find the highest sales order for each customer. (Subquery)
SELECT 
    customer_id,
    order_id,
    sales AS highest_sales
FROM orders o
WHERE sales = (
    SELECT MAX(sales)
    FROM orders sub
    WHERE sub.customer_id = o.customer_id
)
ORDER BY customer_id;
GO

-- Query 3: Calculate total sales for each customer. (CTE)
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT 
    customer_id, 
    total_sales
FROM CustomerSales
ORDER BY total_sales DESC;
GO

-- Query 4: Find customers whose total sales are above average. (CTE + Subquery)
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT 
    customer_id, 
    total_sales
FROM CustomerSales
WHERE total_sales > (
    SELECT AVG(total_sales)
    FROM CustomerSales
)
ORDER BY total_sales DESC;
GO

-- Query 5: Rank all customers based on total sales. (Window Function)
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT 
    customer_id, 
    total_sales,
    DENSE_RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
FROM CustomerSales
ORDER BY sales_rank;
GO

-- Query 6: Assign row numbers to each order within a customer. (Window Function + PARTITION BY)
SELECT 
    customer_id, 
    order_id, 
    order_date, 
    sales,
    ROW_NUMBER() OVER (
        PARTITION BY customer_id 
        ORDER BY order_date, row_id
    ) AS order_row_num
FROM orders
ORDER BY customer_id, order_row_num;
GO

-- Query 7: Display top 3 customers based on total sales. (Window Function)
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
),
RankedCustomers AS (
    SELECT 
        customer_id, 
        total_sales,
        DENSE_RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
    FROM CustomerSales
)
SELECT 
    customer_id, 
    total_sales, 
    sales_rank
FROM RankedCustomers
WHERE sales_rank <= 3
ORDER BY sales_rank;
GO

-- ==========================================
-- STEP 3: FINAL COMBINED QUERY
-- ==========================================
-- Customer Name, Total Sales, Rank (Use JOIN + CTE + Window Function together)
WITH CustomerTotalSales AS (
    SELECT 
        customer_id, 
        SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.customer_name,
    cts.total_sales,
    DENSE_RANK() OVER (ORDER BY cts.total_sales DESC) AS customer_rank
FROM CustomerTotalSales cts
JOIN customers c ON cts.customer_id = c.customer_id
ORDER BY customer_rank;
GO

-- ==========================================
-- MINI PROJECT: CUSTOMER SALES INSIGHTS
-- ==========================================

-- 1. Who are the top 5 customers?
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT TOP 5 
    c.customer_name, 
    cs.total_sales
FROM CustomerSales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales DESC;
GO

-- 2. Who are the bottom 5 customers?
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT TOP 5 
    c.customer_name, 
    cs.total_sales
FROM CustomerSales cs
JOIN customers c ON cs.customer_id = c.customer_id
ORDER BY cs.total_sales ASC;
GO

-- 3. Which customers made only one order?
SELECT 
    c.customer_name, 
    COUNT(DISTINCT o.order_id) AS distinct_order_count
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
HAVING COUNT(DISTINCT o.order_id) = 1
ORDER BY c.customer_name;
GO

-- 4. Which customers have above-average sales?
WITH CustomerSales AS (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.customer_name, 
    cs.total_sales
FROM CustomerSales cs
JOIN customers c ON cs.customer_id = c.customer_id
WHERE cs.total_sales > (
    SELECT AVG(total_sales)
    FROM CustomerSales
)
ORDER BY cs.total_sales DESC;
GO

-- 5. What is the highest order value per customer?
WITH OrderValues AS (
    SELECT 
        customer_id, 
        order_id, 
        SUM(sales) AS order_value
    FROM orders
    GROUP BY customer_id, order_id
)
SELECT 
    c.customer_name, 
    MAX(ov.order_value) AS highest_order_value
FROM OrderValues ov
JOIN customers c ON ov.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY highest_order_value DESC;
GO
