import json
from collections import Counter
from itertools import combinations

def get_frequent_pairs(purchase_file, top_n=10):
    try:
        with open(purchase_file, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    pair_counter = Counter()

    for user_purchases in data.values():
        product_ids = list({p['product_id'] for p in user_purchases})
        if len(product_ids) >= 2:
            for pair in combinations(product_ids, 2):
                sorted_pair = tuple(sorted(pair))
                pair_counter[sorted_pair] += 1

    # Get top N most common products (flattened into a set of IDs)
    top_pairs = pair_counter.most_common(top_n)
    top_product_ids = set()
    for pair, _ in top_pairs:
        top_product_ids.update(pair)

    return list(top_product_ids)
