import os
import re
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

report_lines = []

def log(message):
    print(message)
    report_lines.append(message)

def parse_dates(series, cutoff=None):
    if cutoff is None:
        cutoff = datetime.now()
    parsed = pd.to_datetime(series, errors='coerce', format='mixed', dayfirst=True)
    parsed = parsed.apply(lambda d: d if pd.notnull(d) and d <= cutoff else pd.NaT)
    return parsed.dt.strftime('%Y-%m-%d')

def validate_emails(df_customers):
    invalid_ids = []
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    for idx, row in df_customers.iterrows():
        email = row.get('email')
        cid = row.get('customer_id')
        if pd.isna(email) or not isinstance(email, str) or not re.match(email_regex, email.strip()):
            invalid_ids.append(cid)
            
    log(f"validate_emails(): Found {len(invalid_ids)} customers with invalid/missing emails.")
    return invalid_ids

def check_referential_integrity():
    orders_df = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
    products_df = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
    items_df = pd.read_csv(os.path.join(RAW_DIR, "order_items.csv"))
    
    valid_order_ids = set(orders_df['order_id'].dropna().unique())
    valid_product_ids = set(products_df['product_id'].dropna().unique())
    
    orphaned_orders = items_df[~items_df['order_id'].isin(valid_order_ids)]
    orphaned_products = items_df[~items_df['product_id'].isin(valid_product_ids)]
    
    log(f"check_referential_integrity(): {len(orphaned_orders)} order_items reference non-existent order_ids.")
    log(f"check_referential_integrity(): {len(orphaned_products)} order_items reference non-existent product_ids.")
    
    return {
        'orphaned_order_items': orphaned_orders['item_id'].tolist(),
        'orphaned_product_items': orphaned_products['item_id'].tolist()
    }

def clean_customers():
    raw_path = os.path.join(RAW_DIR, "customers.csv")
    if not os.path.exists(raw_path):
        return pd.DataFrame()
        
    df = pd.read_csv(raw_path)
    start_len = len(df)
    
    df.drop_duplicates(subset=['customer_id'], keep='first', inplace=True)
    df['name'] = df['name'].fillna('Unknown').astype(str).str.strip()
    df['email'] = df['email'].fillna('').astype(str).str.strip().str.lower()
    df['email'] = df['email'].replace({'nan': None, 'none': None, '': None})
    df['location'] = df['location'].fillna('Unknown')
    df['segment'] = df['segment'].fillna('Consumer')
    
    df['join_date'] = parse_dates(df['join_date'])
    df = df[df['join_date'].notnull()].copy()
    
    log(f"clean_customers(): Raw {start_len} rows -> Cleaned {len(df)} rows.")
    return df

def clean_products():
    raw_path = os.path.join(RAW_DIR, "products.csv")
    if not os.path.exists(raw_path):
        return pd.DataFrame()
        
    df = pd.read_csv(raw_path)
    start_len = len(df)
    
    df.drop_duplicates(subset=['product_id'], keep='first', inplace=True)
    df['category'] = df['category'].fillna('General')
    df['product_name'] = df['product_name'].fillna('Unknown Product').astype(str).str.strip().str.title()
    df['category'] = df['category'].astype(str).str.strip().str.title()
    df['category'] = df['category'].replace({'Nan': 'General', 'None': 'General', '': 'General'})
    
    df = df[(df['price'] > 0) & (df['cost'] >= 0)].copy()
    
    log(f"clean_products(): Raw {start_len} rows -> Cleaned {len(df)} rows.")
    return df

def clean_orders(valid_customer_ids):
    raw_path = os.path.join(RAW_DIR, "orders.csv")
    if not os.path.exists(raw_path):
        return pd.DataFrame()
        
    df = pd.read_csv(raw_path)
    start_len = len(df)
    
    df.drop_duplicates(subset=['order_id'], keep='first', inplace=True)
    df['order_date'] = parse_dates(df['order_date'])
    df = df[df['order_date'].notnull()].copy()
    df = df[df['customer_id'].isin(valid_customer_ids)].copy()
    
    valid_statuses = {'Completed', 'Pending', 'Cancelled', 'Returned'}
    df['order_status'] = df['order_status'].apply(lambda s: s if s in valid_statuses else 'Pending')
    
    log(f"clean_orders(): Raw {start_len} rows -> Cleaned {len(df)} rows.")
    return df

def clean_order_items(valid_order_ids, valid_product_ids):
    raw_path = os.path.join(RAW_DIR, "order_items.csv")
    if not os.path.exists(raw_path):
        return pd.DataFrame()
        
    df = pd.read_csv(raw_path)
    start_len = len(df)
    
    df.drop_duplicates(subset=['item_id'], keep='first', inplace=True)
    df = df[(df['quantity'] > 0) & (df['unit_price'] >= 0)].copy()
    df = df[df['order_id'].isin(valid_order_ids) & df['product_id'].isin(valid_product_ids)].copy()
    
    log(f"clean_order_items(): Raw {start_len} rows -> Cleaned {len(df)} rows.")
    return df

def main():
    report_lines.clear()
    log("DATA CLEANING & INTEGRITY REPORT")
    
    check_referential_integrity()
    customers_raw = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    validate_emails(customers_raw)
    
    customers = clean_customers()
    products = clean_products()
    orders = clean_orders(set(customers['customer_id']))
    order_items = clean_order_items(set(orders['order_id']), set(products['product_id']))
    
    customers.to_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), index=False)
    products.to_csv(os.path.join(CLEAN_DIR, "products_clean.csv"), index=False)
    orders.to_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"), index=False)
    order_items.to_csv(os.path.join(CLEAN_DIR, "order_items_clean.csv"), index=False)
    
    report_path = os.path.join(OUTPUT_DIR, "cleaning_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"Cleaned datasets saved to data/cleaned/ and report saved to {report_path}")

if __name__ == "__main__":
    main()
