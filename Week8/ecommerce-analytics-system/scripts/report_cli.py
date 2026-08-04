import argparse
import os
import sqlite3
import sys
import pandas as pd
from tabulate import tabulate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "ecommerce.db")
SQL_DIR = os.path.join(BASE_DIR, "sql")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")

def init_db(db_path=DEFAULT_DB_PATH):
    schema_path = os.path.join(SQL_DIR, "schema.sql")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema missing at {schema_path}")
        
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
        
    tables = {
        'customers': os.path.join(CLEAN_DIR, 'customers_clean.csv'),
        'products': os.path.join(CLEAN_DIR, 'products_clean.csv'),
        'orders': os.path.join(CLEAN_DIR, 'orders_clean.csv'),
        'order_items': os.path.join(CLEAN_DIR, 'order_items_clean.csv')
    }
    
    for table, csv_path in tables.items():
        if os.path.exists(csv_path):
            pd.read_csv(csv_path).to_sql(table, conn, if_exists='append', index=False)
            
    conn.commit()
    conn.close()

def get_connection(db_path=DEFAULT_DB_PATH, rebuild=False):
    if rebuild or not os.path.exists(db_path):
        init_db(db_path)
    return sqlite3.connect(db_path)

def execute_query(conn, query, params=None):
    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        print(f"Database Query Error: {e}", file=sys.stderr)
        return pd.DataFrame()

def report_revenue(conn, limit=10):
    query = """
    SELECT 
        strftime('%Y-%m', o.order_date) AS month,
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS active_buyers,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY month
    ORDER BY month ASC
    LIMIT ?;
    """
    return execute_query(conn, query, (limit,))

def report_top_customers(conn, limit=10):
    query = """
    WITH customer_spend AS (
        SELECT 
            c.customer_id,
            c.name,
            c.segment,
            COUNT(DISTINCT o.order_id) AS total_orders,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS lifetime_value
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY c.customer_id, c.name, c.segment
    )
    SELECT 
        customer_id,
        name,
        segment,
        total_orders,
        lifetime_value,
        DENSE_RANK() OVER (ORDER BY lifetime_value DESC) AS ltv_rank
    FROM customer_spend
    ORDER BY ltv_rank ASC
    LIMIT ?;
    """
    return execute_query(conn, query, (limit,))

def report_retention(conn, limit=12):
    query = """
    WITH first_purchases AS (
        SELECT 
            customer_id,
            MIN(strftime('%Y-%m', order_date)) AS cohort_month
        FROM orders
        WHERE order_status = 'Completed'
        GROUP BY customer_id
    ),
    customer_activities AS (
        SELECT DISTINCT
            o.customer_id,
            fp.cohort_month,
            (CAST(substr(strftime('%Y-%m', o.order_date), 1, 4) AS INT) - CAST(substr(fp.cohort_month, 1, 4) AS INT)) * 12 +
            (CAST(substr(strftime('%Y-%m', o.order_date), 6, 2) AS INT) - CAST(substr(fp.cohort_month, 6, 2) AS INT)) AS month_number
        FROM orders o
        JOIN first_purchases fp ON o.customer_id = fp.customer_id
        WHERE o.order_status = 'Completed'
    ),
    cohort_sizes AS (
        SELECT 
            cohort_month,
            COUNT(DISTINCT customer_id) AS total_cohort_customers
        FROM first_purchases
        GROUP BY cohort_month
    )
    SELECT 
        ca.cohort_month,
        cs.total_cohort_customers,
        ca.month_number,
        COUNT(DISTINCT ca.customer_id) AS active_customers,
        ROUND(CAST(COUNT(DISTINCT ca.customer_id) AS REAL) / cs.total_cohort_customers * 100.0, 2) AS retention_rate_pct
    FROM customer_activities ca
    JOIN cohort_sizes cs ON ca.cohort_month = cs.cohort_month
    GROUP BY ca.cohort_month, cs.total_cohort_customers, ca.month_number
    ORDER BY ca.cohort_month ASC, ca.month_number ASC
    LIMIT ?;
    """
    return execute_query(conn, query, (limit,))

def report_rfm(conn, limit=15):
    query = """
    WITH customer_rfm_raw AS (
        SELECT 
            c.customer_id,
            c.name,
            c.segment AS raw_segment,
            COUNT(DISTINCT o.order_id) AS frequency,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS monetary
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY c.customer_id, c.name, c.segment
    ),
    rfm_scores AS (
        SELECT 
            customer_id,
            name,
            raw_segment,
            frequency,
            monetary,
            CASE 
                WHEN frequency = 1 THEN 'One-Time'
                WHEN frequency BETWEEN 2 AND 4 THEN 'Occasional'
                ELSE 'Loyal'
            END AS frequency_tier,
            CASE 
                WHEN monetary < 500 THEN 'Low Spend'
                WHEN monetary BETWEEN 500 AND 2000 THEN 'Medium Spend'
                ELSE 'High Spend'
            END AS spend_tier
        FROM customer_rfm_raw
    )
    SELECT 
        customer_id,
        name,
        raw_segment,
        frequency,
        monetary,
        frequency_tier,
        spend_tier,
        CASE 
            WHEN frequency_tier = 'Loyal' AND spend_tier = 'High Spend' THEN 'Champions'
            WHEN frequency_tier = 'Loyal' THEN 'Loyal Customers'
            WHEN frequency_tier = 'Occasional' AND spend_tier IN ('Medium Spend', 'High Spend') THEN 'Potential Loyalists'
            WHEN frequency_tier = 'One-Time' AND spend_tier = 'High Spend' THEN 'Big Spenders'
            ELSE 'Recent / Need Nurturing'
        END AS rfm_segment
    FROM rfm_scores
    ORDER BY monetary DESC
    LIMIT ?;
    """
    return execute_query(conn, query, (limit,))

def report_category(conn, limit=10):
    query = """
    SELECT 
        p.category,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(oi.quantity) AS total_units_sold,
        ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
        ROUND(AVG(oi.unit_price), 2) AS avg_selling_price
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY p.category
    ORDER BY total_revenue DESC
    LIMIT ?;
    """
    return execute_query(conn, query, (limit,))

def report_monthly_growth(conn, limit=12):
    query = """
    WITH monthly_sales AS (
        SELECT 
            strftime('%Y-%m', o.order_date) AS rev_month,
            ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY rev_month
    ),
    monthly_lag AS (
        SELECT 
            rev_month,
            total_revenue,
            LAG(total_revenue, 1) OVER (ORDER BY rev_month) AS previous_month_revenue
        FROM monthly_sales
    )
    SELECT 
        rev_month,
        total_revenue,
        COALESCE(previous_month_revenue, 0) AS prev_month_revenue,
        ROUND(total_revenue - COALESCE(previous_month_revenue, total_revenue), 2) AS mom_change,
        ROUND(
            CASE 
                WHEN previous_month_revenue IS NULL OR previous_month_revenue = 0 THEN 0.0
                ELSE ((total_revenue - previous_month_revenue) / previous_month_revenue) * 100.0
            END, 
            2
        ) AS mom_growth_pct
    FROM monthly_lag
    ORDER BY rev_month ASC
    LIMIT ?;
    """
    return execute_query(conn, query, (limit,))

def main():
    parser = argparse.ArgumentParser(description="E-Commerce SQL Analytics & Reporting CLI")
    parser.add_argument(
        "--report", 
        type=str, 
        required=True,
        choices=["revenue", "top_customers", "retention", "rfm", "category", "monthly_growth"],
        help="Report type"
    )
    parser.add_argument("--limit", type=int, default=10, help="Max rows to display")
    parser.add_argument("--db", type=str, default=DEFAULT_DB_PATH, help="SQLite DB path")
    parser.add_argument("--rebuild-db", action="store_true", help="Rebuild database from cleaned CSVs")
    parser.add_argument("--save", type=str, nargs="?", const="default", help="Save report output to text file")
    
    args = parser.parse_args()
    
    if args.limit <= 0:
        print("Error: --limit must be greater than 0.", file=sys.stderr)
        sys.exit(1)
        
    conn = get_connection(args.db, rebuild=args.rebuild_db)
    
    handlers = {
        "revenue": ("Monthly Revenue Summary", report_revenue),
        "top_customers": ("Top Customers by Lifetime Value (LTV)", report_top_customers),
        "retention": ("Cohort Monthly Retention Rate Analysis", report_retention),
        "rfm": ("RFM Customer Segmentation Analysis", report_rfm),
        "category": ("Product Category Performance", report_category),
        "monthly_growth": ("Month-over-Month (MoM) Revenue Growth Rate", report_monthly_growth)
    }
    
    title, fn = handlers[args.report]
    df = fn(conn, args.limit)
    conn.close()
    
    lines = [
        "",
        "=" * 80,
        f" REPORT: {title.upper()}",
        "=" * 80
    ]
    
    if df.empty:
        lines.append("No matching records found.")
    else:
        lines.append(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
    lines.append("=" * 80)
    lines.append("")
    
    output_text = "\n".join(lines)
    print(output_text)
    
    if args.save is not None:
        if args.save == "default":
            out_dir = os.path.join(BASE_DIR, "output", "sample_reports")
            os.makedirs(out_dir, exist_ok=True)
            save_path = os.path.join(out_dir, f"{args.report}_report.txt")
        else:
            save_path = args.save
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Saved report to: {save_path}")

if __name__ == "__main__":
    main()
