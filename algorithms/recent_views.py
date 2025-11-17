import json
from datetime import datetime

def get_recent_views(username, activity_file, top_n=10):
    try:
        with open(activity_file, 'r') as f:
            activity = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    if username not in activity:
        return []

    user_actions = activity[username]
    
    # Filter for 'view' actions with proper timestamps
    views = [
        entry for entry in user_actions
        if entry.get('action') == 'view' and 'timestamp' in entry and 'product_id' in entry
    ]

    # Sort by timestamp (most recent first)
    try:
        views.sort(key=lambda x: datetime.fromisoformat(x['timestamp']), reverse=True)
    except ValueError:
        return []

    seen = set()
    recent = []

    # Collect unique product_ids in order
    for v in views:
        pid = v['product_id']
        if pid not in seen:
            seen.add(pid)
            recent.append(pid)
        if len(recent) == top_n:
            break

    return recent
