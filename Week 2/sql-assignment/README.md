# Relational SQL Database Assignment

This repository contains the structured SQL queries and database setup scripts for the Superstore relational database assignment.

## Repository Structure

```
sql-assignment/
│── Section_A/
│   └── basic_queries.sql
│── Section_B/
│   └── filtering_queries.sql
│── Section_C/
│   └── aggregation_queries.sql
│── Section_D/
│   └── joins_queries.sql
│── Section_E/
│   └── advanced_queries.sql
└── README.md
```

---

## Database Schema & ER Model

The relational database model follows normalized 3NF principles across 4 related tables:

1. **`customers`**: Stores customer demographical and location data.
   - Primary Key: `customer_id`
2. **`products`**: Stores inventory catalog details.
   - Primary Key: `product_id`
3. **`orders`**: Header record for customer purchase transactions.
   - Primary Key: `order_id`
   - Foreign Key: `customer_id` -> `customers(customer_id)`
4. **`order_items`**: Transaction line items detail (sales, discount, quantity, profit).
   - Primary Key: `item_id`
   - Foreign Keys: `order_id` -> `orders(order_id)`, `product_id` -> `products(product_id)`

---

## Section Summaries

### Section A – Database Setup & Basics (`Section_A/basic_queries.sql`)
- **DDL Creation**: Table creation scripts enforcing Primary Key & Foreign Key constraints.
- **Indexes**: Query performance optimization via single and composite indexes.
- **DML Inserts**: Initial population with verified data records.
- **Validation**: Record count integrity checks and baseline `SELECT` operations.

### Section B – Data Filtering (`Section_B/filtering_queries.sql`)
- `WHERE` clause conditions using `=`, `>`, `<`, `BETWEEN`, `IN`, `LIKE`, and logical operators.
- Filtering sales transactions, region specific criteria, date ranges, and profit threshold analysis.

### Section C – Aggregation & Grouping (`Section_C/aggregation_queries.sql`)
- Summary statistics using `COUNT()`, `SUM()`, `AVG()`, `MIN()`, and `MAX()`.
- Segment and category analysis using `GROUP BY` and `HAVING` clauses.

### Section D – SQL Joins (`Section_D/joins_queries.sql`)
- Multi-table relational queries utilizing `INNER JOIN` and `LEFT JOIN`.
- Relational mapping between customer profiles, order headers, line items, and product catalog metadata.

### Section E – Advanced SQL Techniques (`Section_E/advanced_queries.sql`)
- Conditional categorization using `CASE` expressions.
- CTEs (Common Table Expressions) and subqueries for layered analytics.
- Window functions (`ROW_NUMBER()`, `DENSE_RANK()`).
- Data modification within atomic database transactions (`BEGIN TRANSACTION` / `COMMIT`).

---

## Execution Instructions

1. Open your preferred SQL RDBMS tool (MySQL, PostgreSQL, Microsoft SQL Server, or SQLite).
2. Execute `Section_A/basic_queries.sql` to build the database schema, indexes, and initial dataset.
3. Run queries in sequence from `Section_B` through `Section_E`.
