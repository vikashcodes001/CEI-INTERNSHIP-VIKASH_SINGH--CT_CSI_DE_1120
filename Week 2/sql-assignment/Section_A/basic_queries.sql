-- Section A: Database Setup, Schema Definition & Basic Queries

-- 1. Create Tables in relational order

CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    segment VARCHAR(100) NOT NULL,
    country VARCHAR(100) DEFAULT 'United States',
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(100)
);

CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL,
    product_name VARCHAR(500) NOT NULL
);

CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    ship_mode VARCHAR(100) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id INT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    sales DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    discount DECIMAL(4, 2) NOT NULL DEFAULT 0.00,
    profit DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 2. Create Indexes for performance optimization

CREATE INDEX idx_customers_region ON customers(region);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_items_order ON order_items(order_id);
CREATE INDEX idx_items_product ON order_items(product_id);

-- 3. Data Insertion

INSERT INTO customers (customer_id, customer_name, segment, country, city, state, postal_code, region) VALUES
('CG-12520', 'Claire Gute', 'Consumer', 'United States', 'Henderson', 'Kentucky', '42420', 'South'),
('DV-13045', 'Darrin Van Huff', 'Corporate', 'United States', 'Los Angeles', 'California', '90036', 'West'),
('SO-20335', 'Sean O''Donnell', 'Consumer', 'United States', 'Fort Lauderdale', 'Florida', '33311', 'South'),
('BH-11710', 'Brosina Hoffman', 'Consumer', 'United States', 'Los Angeles', 'California', '90032', 'West'),
('AA-10250', 'Aaron Bergman', 'Corporate', 'United States', 'Seattle', 'Washington', '98103', 'West');

INSERT INTO products (product_id, category, sub_category, product_name) VALUES
('FUR-BO-10001798', 'Furniture', 'Bookcases', 'Bush Somerset Collection Bookcase'),
('FUR-CH-10000454', 'Furniture', 'Chairs', 'Hon Deluxe Fabric Upholstered Stacking Chairs'),
('OFF-LA-10000240', 'Office Supplies', 'Labels', 'Self-Adhesive Address Labels'),
('FUR-TA-10000577', 'Furniture', 'Tables', 'Bretford CR4500 Series Conference Table'),
('OFF-ST-10000760', 'Office Supplies', 'Storage', 'Eldon Fold ''N Files Storage Box');

INSERT INTO orders (order_id, customer_id, order_date, ship_date, ship_mode) VALUES
('CA-2016-152156', 'CG-12520', '2016-11-08', '2016-11-11', 'Second Class'),
('CA-2016-138688', 'DV-13045', '2016-06-12', '2016-06-16', 'Second Class'),
('US-2015-108966', 'SO-20335', '2015-10-11', '2015-10-18', 'Standard Class'),
('CA-2014-115812', 'BH-11710', '2014-06-09', '2014-06-14', 'Standard Class'),
('CA-2017-114412', 'AA-10250', '2017-04-15', '2017-04-20', 'Standard Class');

INSERT INTO order_items (item_id, order_id, product_id, sales, quantity, discount, profit) VALUES
(1, 'CA-2016-152156', 'FUR-BO-10001798', 261.96, 2, 0.00, 41.91),
(2, 'CA-2016-152156', 'FUR-CH-10000454', 731.94, 3, 0.00, 219.58),
(3, 'CA-2016-138688', 'OFF-LA-10000240', 14.62, 2, 0.00, 6.87),
(4, 'US-2015-108966', 'FUR-TA-10000577', 957.57, 5, 0.45, -383.03),
(5, 'CA-2014-115812', 'OFF-ST-10000760', 22.36, 2, 0.20, 2.52);

-- 4. Data Validation

SELECT COUNT(*) AS customer_count FROM customers;
SELECT COUNT(*) AS product_count FROM products;
SELECT COUNT(*) AS order_count FROM orders;
SELECT COUNT(*) AS order_item_count FROM order_items;

-- 5. Basic SELECT Queries

SELECT * FROM customers;

SELECT product_id, product_name, category, sub_category 
FROM products;

SELECT order_id, customer_id, order_date, ship_mode 
FROM orders;
