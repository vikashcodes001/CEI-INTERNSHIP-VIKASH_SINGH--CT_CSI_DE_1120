import argparse
import datetime
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "ecommerce.db")

def parse_date(date_str):
    try:
        return datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Please use YYYY-MM-DD.")

def calculate_previous_period(start_date, end_date):
    duration = (end_date - start_date).days + 1
    prev_end = start_date - datetime.timedelta(days=1)
    prev_start = prev_end - datetime.timedelta(days=duration - 1)
    return prev_start, prev_end

def get_period_metrics(conn, start_date, end_date):
    query = """
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            COALESCE(SUM(oi.quantity * oi.unit_price), 0.0) AS total_revenue,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_date >= ? AND o.order_date <= ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
    row = cursor.fetchone()
    return {
        "orders": row[0] or 0,
        "revenue": row[1] or 0.0,
        "customers": row[2] or 0
    }

def get_top_3_products(conn, start_date, end_date):
    query = """
        SELECT 
            p.product_name,
            SUM(oi.quantity) AS total_qty,
            SUM(oi.quantity * oi.unit_price) AS total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.order_date >= ? AND o.order_date <= ?
        GROUP BY p.product_id, p.product_name
        ORDER BY total_revenue DESC
        LIMIT 3
    """
    cursor = conn.cursor()
    cursor.execute(query, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
    return cursor.fetchall()

def pct_change(current, previous):
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return ((current - previous) / previous) * 100.0

def generate_report(period_type, start_date, end_date, db_path=DEFAULT_DB_PATH):
    if not os.path.exists(db_path):
        print(f"Error: Database not found at '{db_path}'.", file=sys.stderr)
        return

    conn = sqlite3.connect(db_path)
    prev_start, prev_end = calculate_previous_period(start_date, end_date)
    
    curr_metrics = get_period_metrics(conn, start_date, end_date)
    prev_metrics = get_period_metrics(conn, prev_start, prev_end)
    top_products = get_top_3_products(conn, start_date, end_date)
    conn.close()

    orders_change = pct_change(curr_metrics["orders"], prev_metrics["orders"])
    revenue_change = pct_change(curr_metrics["revenue"], prev_metrics["revenue"])
    customers_change = pct_change(curr_metrics["customers"], prev_metrics["customers"])

    print(f"\nE-COMMERCE ANALYTICS REPORT ({period_type.upper()})")
    print(f"Current Period  : {start_date} to {end_date}")
    print(f"Previous Period : {prev_start} to {prev_end}")
    print("-" * 65)
    print("SUMMARY METRICS:")
    print(f"  - Total Orders           : {curr_metrics['orders']:,} (vs prev: {prev_metrics['orders']:,}, Change: {orders_change:+.2f}%)")
    print(f"  - Total Revenue          : ${curr_metrics['revenue']:,.2f} (vs prev: ${prev_metrics['revenue']:,.2f}, Change: {revenue_change:+.2f}%)")
    print(f"  - Unique Active Customers: {curr_metrics['customers']:,} (vs prev: {prev_metrics['customers']:,}, Change: {customers_change:+.2f}%)")
    print("-" * 65)
    print("TOP 3 PRODUCTS BY REVENUE:")
    if not top_products:
        print("  No product sales in this period.")
    else:
        for idx, (pname, qty, rev) in enumerate(top_products, start=1):
            print(f"  {idx}. {pname} - {qty} units sold, ${rev:,.2f} revenue")
    print()

def main():
    parser = argparse.ArgumentParser(description="E-Commerce CLI Reporting Tool")
    parser.add_argument("--period", choices=["daily", "weekly", "monthly"], help="Report type (daily/weekly/monthly)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help="Path to SQLite database file")
    
    args = parser.parse_args()
    
    period = args.period
    if not period:
        while True:
            period_input = input("Enter report type (daily/weekly/monthly): ").strip().lower()
            if period_input in ["daily", "weekly", "monthly"]:
                period = period_input
                break
            print("Invalid input. Please enter 'daily', 'weekly', or 'monthly'.")
            
    start_str = args.start
    if not start_str:
        start_str = input("Enter start date (YYYY-MM-DD): ").strip()
        
    end_str = args.end
    if not end_str:
        end_str = input("Enter end date (YYYY-MM-DD): ").strip()
        
    try:
        start_date = parse_date(start_str)
        end_date = parse_date(end_str)
        if start_date > end_date:
            print("Error: Start date cannot be after end date.", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
        
    generate_report(period, start_date, end_date, db_path=args.db)

if __name__ == "__main__":
    main()
