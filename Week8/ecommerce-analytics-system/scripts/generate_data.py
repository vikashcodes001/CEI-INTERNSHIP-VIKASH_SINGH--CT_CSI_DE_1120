import os
import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

fake = Faker()
random.seed(42)
Faker.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

def generate_customers(count=200):
    segments = ['Consumer', 'Corporate', 'Small Business']
    locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX', 'Phoenix, AZ', 'Miami, FL', 'Seattle, WA']
    
    rows = []
    start = datetime(2023, 1, 1)
    
    for i in range(1, count + 1):
        dt = start + timedelta(days=random.randint(0, 500))
        
        if i % 15 == 0:
            date_str = dt.strftime("%d/%m/%Y")
        elif i % 25 == 0:
            date_str = "2027-12-31"
        else:
            date_str = dt.strftime("%Y-%m-%d")
            
        name = fake.name()
        if i % 10 == 0:
            name = f"  {name}   "
            
        email = fake.email() if i % 12 != 0 else None
        location = random.choice(locations) if i % 14 != 0 else None
        
        rows.append({
            'customer_id': i,
            'name': name,
            'email': email,
            'join_date': date_str,
            'segment': random.choice(segments),
            'location': location
        })
        
    df = pd.DataFrame(rows)
    duplicates = df.sample(n=5, random_state=42).copy()
    return pd.concat([df, duplicates], ignore_index=True)

def generate_products():
    catalog = [
        ('Wireless Noise-Canceling Headphones', 'Electronics', 199.99, 110.00),
        ('Mechanical Gaming Keyboard', 'Electronics', 89.50, 45.00),
        ('Ultra-Wide Monitor 34-inch', 'Electronics', 449.00, 280.00),
        ('USB-C Fast Charging Cable', 'Electronics', 14.99, 3.50),
        ('Smart Fitness Watch', 'Electronics', 129.95, 65.00),
        ('Cotton Graphic T-Shirt', 'Apparel', 24.99, 8.00),
        ('Slim-Fit Denim Jeans', 'Apparel', 59.99, 22.00),
        ('All-Weather Hooded Jacket', 'Apparel', 89.00, 38.00),
        ('Running Performance Sneakers', 'Apparel', 110.00, 50.00),
        ('Stainless Steel Travel Mug', 'Home & Kitchen', 19.99, 6.00),
        ('Non-Stick Ceramic Frying Pan', 'Home & Kitchen', 34.50, 14.00),
        ('Automatic Drip Coffee Maker', 'Home & Kitchen', 79.99, 35.00),
        ('Ergonomic Memory Foam Pillow', 'Home & Kitchen', 29.99, 10.00),
        ('Data Science in Python Handbook', 'Books', 45.00, 18.00),
        ('Designing Data-Intensive Applications', 'Books', 52.00, 22.00),
        ('Clean Code: Modern Principles', 'Books', 39.99, 15.00),
        ('Adjustable Dumbbell Set 50lbs', 'Fitness', 180.00, 95.00),
        ('Non-Slip Yoga Mat', 'Fitness', 29.99, 9.00),
        ('Resistance Bands Set', 'Fitness', 18.50, 5.00),
        ('Hydrating Facial Moisturizer', 'Beauty', 22.00, 7.00)
    ]
    
    rows = []
    for idx, (pname, cat, price, cost) in enumerate(catalog, start=101):
        if idx == 105:
            price = -25.00
        elif idx == 110:
            cat = None
        elif idx == 115:
            price = 0.0
            
        rows.append({
            'product_id': idx,
            'product_name': pname,
            'category': cat,
            'price': price,
            'cost': cost
        })
        
    df = pd.DataFrame(rows)
    return pd.concat([df, df.iloc[[2]]], ignore_index=True)

def generate_orders(customers_df, count=600):
    statuses = ['Completed', 'Completed', 'Completed', 'Pending', 'Cancelled', 'Returned']
    payments = ['Credit Card', 'PayPal', 'Debit Card', 'Apple Pay']
    cust_ids = customers_df['customer_id'].dropna().unique().tolist()
    
    rows = []
    start = datetime(2024, 1, 1)
    
    for i in range(1001, 1001 + count):
        dt = start + timedelta(days=random.randint(0, 180))
        
        if i % 20 == 0:
            date_str = None
        elif i % 35 == 0:
            date_str = "2029-06-15"
        elif i % 15 == 0:
            date_str = dt.strftime("%d-%m-%Y")
        else:
            date_str = dt.strftime("%Y-%m-%d")
            
        cid = random.choice(cust_ids) if i % 40 != 0 else 99999
        
        rows.append({
            'order_id': i,
            'customer_id': cid,
            'order_date': date_str,
            'order_status': random.choice(statuses),
            'payment_method': random.choice(payments)
        })
        
    df = pd.DataFrame(rows)
    duplicates = df.sample(n=4, random_state=42).copy()
    return pd.concat([df, duplicates], ignore_index=True)

def generate_order_items(orders_df, products_df):
    order_ids = orders_df['order_id'].dropna().unique().tolist()
    prices = products_df.set_index('product_id')['price'].to_dict()
    prod_ids = list(prices.keys())
    
    rows = []
    item_id = 1
    
    for oid in order_ids:
        item_count = random.randint(1, 4)
        chosen_prods = random.sample(prod_ids, k=min(item_count, len(prod_ids)))
        
        for pid in chosen_prods:
            qty = random.randint(1, 5)
            uprice = prices.get(pid, 25.00)
            
            if item_id % 30 == 0:
                qty = -1
            elif item_id % 45 == 0:
                qty = 0
            elif item_id % 50 == 0:
                pid = 88888
            elif item_id % 70 == 0:
                uprice *= 0.5
                
            rows.append({
                'item_id': item_id,
                'order_id': oid,
                'product_id': pid,
                'quantity': qty,
                'unit_price': round(uprice, 2)
            })
            item_id += 1
            
    rows.append({
        'item_id': item_id,
        'order_id': 77777,
        'product_id': prod_ids[0],
        'quantity': 2,
        'unit_price': 19.99
    })
    
    return pd.DataFrame(rows)

def main():
    print("Generating raw e-commerce data...")
    
    customers = generate_customers(200)
    products = generate_products()
    orders = generate_orders(customers, 600)
    order_items = generate_order_items(orders, products)
    
    customers.to_csv(os.path.join(RAW_DIR, "customers.csv"), index=False)
    products.to_csv(os.path.join(RAW_DIR, "products.csv"), index=False)
    orders.to_csv(os.path.join(RAW_DIR, "orders.csv"), index=False)
    order_items.to_csv(os.path.join(RAW_DIR, "order_items.csv"), index=False)
    
    print("Raw CSV files created successfully in data/raw/")

if __name__ == "__main__":
    main()
