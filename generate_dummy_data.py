import json
import random
import os
from datetime import datetime, timedelta

# Set up the correct data folder
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
print(f"Saving files to: {os.path.abspath(DATA_DIR)}")

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    print(f"✅ Saved {filename} | Size: {os.path.getsize(filename)} bytes")

def generate_data():
    sales = [{
        "product_id": random.randint(1, 500),
        "user_id": f"user_{random.randint(1, 50)}",
        "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%dT%H:%M:%S")
    } for _ in range(1000)]
    save_json(sales, os.path.join(DATA_DIR, "sales.json"))

    views = [{
        "product_id": random.randint(1, 500),
        "user_id": f"user_{random.randint(1, 50)}",
        "timestamp": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%dT%H:%M:%S")
    } for _ in range(2000)]
    save_json(views, os.path.join(DATA_DIR, "views.json"))

    transactions = [{
        "user_id": f"user_{i}",
        "products": random.sample(range(1, 501), random.randint(1, 5))
    } for i in range(1, 51)]
    save_json(transactions, os.path.join(DATA_DIR, "transactions.json"))

    return sales, views, transactions

# Run the generator
sales = generate_data()



