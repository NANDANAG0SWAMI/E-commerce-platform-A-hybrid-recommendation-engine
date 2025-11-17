import json
from collections import Counter
from datetime import datetime, timedelta

def get_trending_products(purchase_file, top_n=10):
    try:
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    # Define the trending window (e.g., past 7 days)
    trending_cutoff = datetime.utcnow() - timedelta(days=7)
    trending_ids = []

    for user_data in purchases.values():
        for entry in user_data:
            timestamp = entry.get('purchased_at')
            if not timestamp:
                continue
            try:
                dt = datetime.fromisoformat(timestamp)
                if dt >= trending_cutoff:
                    product_id = entry.get('product_id')
                    if product_id is not None:
                        trending_ids.append(product_id)
            except Exception:
                continue

    top_trending = [pid for pid, _ in Counter(trending_ids).most_common(top_n)]
    return top_trending
