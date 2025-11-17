import json
from collections import Counter

def get_similar_items(purchase_file, top_n=10):
    try:
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    item_counter = Counter()

    # Count total purchases for each product (excluding per-user filtering)
    for user_purchases in purchases.values():
        for item in user_purchases:
            product_id = item.get('product_id')
            if product_id is not None:
                item_counter[product_id] += 1

    most_common_ids = [pid for pid, _ in item_counter.most_common(top_n)]
    return most_common_ids
