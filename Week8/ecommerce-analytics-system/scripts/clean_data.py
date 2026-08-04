import os
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "cleaned")
os.makedirs(CLEAN_DIR, exist_ok=True)

def parse_dates(series, cutoff=None):
    if cutoff is None:
        cutoff = datetime.now()
    parsed = pd.to_datetime(series, errors='coerce', format='mixed', dayfirst=True)
    parsed = parsed.apply(lambda d: d if pd.notnull(d) and d <= cutoff else pd.NaT)
    return parsed.dt.strftime('%Y-%m-%d')

def clean_customers():
    df = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
    start_len = len(df)
    
    df.drop_duplicates(subset=['customer_id'], keep='first', inplace=True)
    
    df['name'] = df['name'].astype(str).str.strip()
    df['email'] = df['email'].astype(str).str.strip().str.lower()
    df['email'] = df['email'].replace({'nan': None, 'none': None, '': None})
    df['location'] = df['location'].fillna('Unknown')
    df['segment'] = df['segment'].fillna('Consumer')
    
    df['join_date'] = parse_dates(df['join_date'])
    df = df[df['join_date'].notnull()].copy()
    
    print(f"Customers cleaned: {start_len} -> {len(df)} rows")
    return df

def clean_products():
    df = pd.read_csv(os.path.join(RAW_DIR, "products.csv"))
    start_len = len(df)
    
    df.drop_duplicates(subset=['product_id'], keep='first', inplace=True)
    df['category'] = df['category'].fillna('General')
    df = df[(df['price'] > 0) & (df['cost'] >= 0)].copy()
    
    print(f"Products cleaned: {start_len} -> {len(df)} rows")
    return df

def clean_orders(valid_customer_ids):
    df = pd.read_csv(os.path.join(RAW_DIR, "orders.csv"))
    start_len = len(df)
    
    df.drop_duplicates(subset=['order_id'], keep='first', inplace=True)
    df['order_date'] = parse_dates(df['order_date'])
    df = df[df['order_date'].notnull()].copy()
    df = df[df['customer_id'].isin(valid_customer_ids)].copy()
    
    valid_statuses = {'Completed', 'Pending', 'Cancelled', 'Returned'}
    df['order_status'] = df['order_status'].apply(lambda s: s if s in valid_statuses else 'Pending')
    
    print(f"Orders cleaned: {start_len} -> {len(df)} rows")
    return df

def clean_order_items(valid_order_ids, valid_product_ids):
    df = pd.read_csv(os.path.join(RAW_DIR, "order_items.csv"))
    start_len = len(df)
    
    df.drop_duplicates(subset=['item_id'], keep='first', inplace=True)
    df = df[(df['quantity'] > 0) & (df['unit_price'] >= 0)].copy()
    df = df[df['order_id'].isin(valid_order_ids) & df['product_id'].isin(valid_product_ids)].copy()
    
    print(f"Order Items cleaned: {start_len} -> {len(df)} rows")
    return df

def main():
    print("Processing datasets and validating referential integrity...")
    
    customers = clean_customers()
    products = clean_products()
    
    orders = clean_orders(set(customers['customer_id']))
    order_items = clean_order_items(set(orders['order_id']), set(products['product_id']))
    
    customers.to_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), index=False)
    products.to_csv(os.path.join(CLEAN_DIR, "products_clean.csv"), index=False)
    orders.to_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"), index=False)
    order_items.to_csv(os.path.join(CLEAN_DIR, "order_items_clean.csv"), index=False)
    
    print(f"Cleaned files written to data/cleaned/")

if __name__ == "__main__":
    main()
