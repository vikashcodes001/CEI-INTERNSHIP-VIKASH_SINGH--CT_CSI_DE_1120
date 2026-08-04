# End-to-End E-Commerce Order Analytics System

An enterprise data analytics platform built with **Python** (Pandas, Faker, Argparse, Standard Library) and **SQL** (SQLite). This project implements a complete data pipeline from synthetic data generation with intentional anomalies, automated cleaning and referential integrity validation, relational SQL schema design, 16 complex SQL queries (window functions, multi-level CTEs, YoY comparisons, cohort retention, market basket analysis), a standard-library CLI reporting tool, and an edge case test suite.

---

## 1. Directory Structure

```
ecommerce-analytics-system/
│── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   ├── products.csv
│   │   ├── orders.csv
│   │   └── order_items.csv
│   └── cleaned/
│       ├── customers.csv
│       ├── products.csv
│       ├── orders.csv
│       └── order_items.csv
│── scripts/
│   ├── generate_data.py
│   ├── clean_data.py
│   ├── cli_tool.py
│   ├── report_cli.py
│   └── test_edge_cases.py
│── sql/
│   ├── schema.sql
│   ├── queries.sql
│   ├── aggregations.sql
│   ├── window_functions.sql
│   └── cohort_analysis.sql
│── output/
│   ├── cleaning_report.txt
│   └── sample_reports/
│       ├── revenue_report.txt
│       ├── top_customers_report.txt
│       ├── retention_report.txt
│       ├── rfm_report.txt
│       ├── category_report.txt
│       └── monthly_growth_report.txt
└── README.md
```

---

## 2. System Architecture & Data Schemas

### Data Schemas ($\ge 500$ rows per table):

1. **`customers.csv`**:
   - `customer_id` (INTEGER PRIMARY KEY)
   - `customer_name` (TEXT)
   - `email` (TEXT)
   - `registration_date` (DATETIME YYYY-MM-DD HH:MM:SS)
   - `customer_type` (`REGULAR`, `PREMIUM`, `VIP`)

2. **`products.csv`**:
   - `product_id` (INTEGER PRIMARY KEY)
   - `product_name` (TEXT)
   - `category` (TEXT)
   - `subcategory` (TEXT)
   - `cost_price` (REAL)
   - `unit_price` (REAL)

3. **`orders.csv`**:
   - `order_id` (INTEGER PRIMARY KEY)
   - `customer_id` (INTEGER NULLABLE)
   - `order_date` (DATETIME YYYY-MM-DD HH:MM:SS)
   - `status` (`PLACED`, `SHIPPED`, `DELIVERED`, `CANCELLED`, `RETURNED`)
   - `region_code` (TEXT: `NORTH`, `SOUTH`, `EAST`, `WEST`, `CENTRAL`)

4. **`order_items.csv`**:
   - `item_id` (INTEGER PRIMARY KEY)
   - `order_id` (INTEGER)
   - `product_id` (INTEGER)
   - `quantity` (INTEGER, negative = returns)
   - `unit_price` (REAL)
   - `discount_percent` (REAL between 0 and 100)

---

## 3. Data Cleaning & Analytical Functions (`scripts/clean_data.py`)

- **`clean_orders()`**: Standardizes dates to `YYYY-MM-DD HH:MM:SS`, purges NULL `customer_id` rows, and rejects future dates (`2027+`).
- **`clean_products()`**: Trims extra whitespace and converts product names and categories to Title Case.
- **`validate_emails()`**: Identifies and logs customer IDs with malformed emails (missing `@` or domain).
- **`check_referential_integrity()`**: Identifies orphaned `order_items` referencing non-existent `order_id`s.
- **Python Calculations**:
  - Region running revenue totals ordered by date.
  - Category product revenue ranking (ties = same rank).
  - Customer order gap analysis (flags average gap > 30 days as "At Risk").
- Output: Cleaned CSV files + [output/cleaning_report.txt](file:///c:/Users/vs332/Downloads/INTERNSHIP/Week8/ecommerce-analytics-system/output/cleaning_report.txt).

---

## 4. Complete 16 SQL Analytics Queries (`sql/queries.sql`)

1. **Category Net Revenue**: `quantity * unit_price * (1 - discount_percent/100)`.
2. **Top 10 Customers**: Ranked by total order value.
3. **Month-Wise Order Count**: Order volume for last 12 months.
4. **Undelivered Customers**: Customers with orders but zero `DELIVERED` items.
5. **Net Returned Products**: Products with more return quantities than purchases.
6. **Category Return Rates**: `returned items / total items` per category.
7. **Region Running Totals**: Window function cumulative revenue by region over date.
8. **Category Product Ranking**: Product revenue ranking per category with `DENSE_RANK()`.
9. **LAG Order Gap Analysis**: Days gap between consecutive orders per customer.
10. **Multi-Level CTE**: Monthly customer revenue $\rightarrow$ Spend Tier (`High`, `Medium`, `Low`) $\rightarrow$ Monthly Count.
11. **LTV NTILE Segmentation**: 4 LTV quartiles (`Platinum`, `Gold`, `Silver`, `Bronze`).
12. **Year-over-Year (YoY) Growth**: 12-month `LAG` revenue comparison and YoY % growth.
13. **First vs Most Recent Category Shift**: Compares first vs last purchased category (`category_shift = 'Yes'/'No'`).
14. **Cumulative Revenue Pareto Distribution**: Cumulative revenue & percentage contribution from top N% of customers.
15. **Cohort Retention Matrix**: Registration month cohort retention rate across Month 0, 1, 2, 3.
16. **Market Basket Analysis**: Self-join query finding products frequently bought together (excluding duplicates and same-item pairs).

---

## 5. Standard Library CLI Reporting Tool (`scripts/cli_tool.py`)

Built using **only Python standard library (`sqlite3`, `sys`, `datetime`, `argparse`)**:
- Accepts report period (`daily`, `weekly`, `monthly`) and date ranges.
- Displays summary report: Total orders, total net revenue, unique active customers, top 3 products, and period-over-period % change comparison.

### Usage:
```bash
python scripts/cli_tool.py --period monthly --start 2024-01-01 --end 2024-03-31
```

---

## 6. Edge Case Unit Testing Suite (`scripts/test_edge_cases.py`)

Python unit test suite covering 5 critical scenarios:
1. `test_1_orphaned_order_items()`: Verifies orphaned items detection and removal.
2. `test_2_invalid_discount_percent()`: Verifies rejection of discounts > 100%.
3. `test_3_zero_quantity()`: Verifies $0.00 revenue contribution for zero-quantity items.
4. `test_4_future_order_dates()`: Verifies filtering of future dates.
5. `test_5_frequently_bought_together()`: Verifies market basket analysis pair counts.

### Usage:
```bash
python scripts/test_edge_cases.py
```

---

## 7. Execution Guide

```bash
# 1. Generate synthetic raw data (>= 500 rows/table + anomalies)
python scripts/generate_data.py

# 2. Clean data & validate referential integrity
python scripts/clean_data.py

# 3. Populate database & verify 16 SQL queries
python -c "import sqlite3, pandas as pd; conn = sqlite3.connect('ecommerce.db'); conn.executescript(open('sql/schema.sql').read()); [pd.read_csv(f'data/cleaned/{t}.csv').to_sql(t, conn, if_exists='append', index=False) for t in ['customers', 'products', 'orders', 'order_items']]; conn.executescript(open('sql/queries.sql').read())"

# 4. Run Stdlib CLI Summary Report
python scripts/cli_tool.py --period monthly --start 2024-01-01 --end 2024-03-31

# 5. Run Unit Test Suite
python scripts/test_edge_cases.py
```
