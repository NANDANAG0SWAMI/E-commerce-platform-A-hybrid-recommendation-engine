import json
from collections import Counter

def get_bestsellers(purchase_file, top_n=20):
    try:
        with open(purchase_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    # Count frequency of each product_id across all users
    product_counter = Counter()
    for purchases in data.values():
        for purchase in purchases:
            product_id = purchase.get('product_id')
            if product_id:
                product_counter[product_id] += 1

    # Return product_ids sorted from most to least sold
    return [pid for pid, _ in product_counter.most_common(top_n)]
