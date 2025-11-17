import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase
cred_path = r"C:\Users\nanda\OneDrive\Desktop\Recommendation_poc\firebase_hybrec_new_key.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to track user views
def track_view(user_id, product_id):
    db.collection("user_activity").add({
        "user_id": user_id,
        "product_id": product_id,
        "type": "view",
        "timestamp": firestore.SERVER_TIMESTAMP
    })


