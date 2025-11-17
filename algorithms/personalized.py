import json
from collections import Counter

def get_personalized_picks(username, purchase_file, top_n=10):
    try:
        with open(purchase_file, 'r') as f:
            purchases = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    # Get the current user's purchase history
    user_purchases = purchases.get(username, [])
    if not user_purchases:
        return []

    # Count how often each item was purchased by the user
    counter = Counter()
    for item in user_purchases:
        product_id = item.get('product_id')
        if product_id is not None:
            counter[product_id] += 1

    # Get top N purchased products by user
    top_product_ids = [pid for pid, _ in counter.most_common(top_n)]
    return top_product_ids
