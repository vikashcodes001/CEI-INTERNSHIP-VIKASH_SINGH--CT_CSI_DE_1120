import datetime
import os
import sqlite3
import unittest

class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        self.cursor.executescript("""
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                join_date DATE,
                segment TEXT,
                location TEXT
            );

            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK (price >= 0),
                cost REAL NOT NULL CHECK (cost >= 0)
            );

            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                order_status TEXT NOT NULL CHECK (order_status IN ('Completed', 'Pending', 'Cancelled', 'Returned')),
                payment_method TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            );

            CREATE TABLE order_items (
                item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price REAL NOT NULL CHECK (unit_price >= 0),
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
            );
        """)
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_1_orphaned_order_items(self):
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.cursor.execute("INSERT INTO products VALUES (1, 'Test Product', 'Tech', 100.0, 50.0);")
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO order_items VALUES (1, 9999, 1, 2, 100.0);")

    def test_2_invalid_discount_percent(self):
        discount = 150.0
        unit_price = 100.0
        effective_price = max(0.0, unit_price * (1 - min(discount, 100.0) / 100.0))
        self.assertEqual(effective_price, 0.0)

    def test_3_zero_quantity(self):
        self.cursor.execute("INSERT INTO customers VALUES (1, 'John', 'john@test.com', '2024-01-01', 'Consumer', 'US');")
        self.cursor.execute("INSERT INTO orders VALUES (1, 1, '2024-01-02', 'Completed', 'Card');")
        self.cursor.execute("INSERT INTO products VALUES (1, 'Test Product', 'Tech', 100.0, 50.0);")
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("INSERT INTO order_items VALUES (1, 1, 1, 0, 100.0);")

    def test_4_future_order_dates(self):
        today = datetime.date.today()
        future_date = (today + datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        past_date = "2024-01-01"

        self.cursor.execute("INSERT INTO customers VALUES (1, 'John', 'john@test.com', '2024-01-01', 'Consumer', 'US');")
        self.cursor.execute("INSERT INTO orders VALUES (1, 1, ?, 'Completed', 'Card');", (past_date,))
        self.cursor.execute("INSERT INTO orders VALUES (2, 1, ?, 'Completed', 'Card');", (future_date,))
        self.conn.commit()

        self.cursor.execute("SELECT order_id FROM orders WHERE order_date <= ?;", (today.strftime("%Y-%m-%d"),))
        valid_orders = [row[0] for row in self.cursor.fetchall()]
        self.assertIn(1, valid_orders)
        self.assertNotIn(2, valid_orders)

if __name__ == "__main__":
    unittest.main()
