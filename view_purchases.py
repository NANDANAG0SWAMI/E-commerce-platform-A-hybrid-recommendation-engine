import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase
cred_path = r"C:\Users\nanda\OneDrive\Desktop\Recommendation_poc\firebase db\firebase_hybrec_new_key.json"
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to track purchases
def track_purchase(user_id, product_id):
    db.collection("user_activity").add({
        "user_id": user_id,
        "product_id": product_id,
        "type": "purchase",
        "timestamp": firestore.SERVER_TIMESTAMP
    })

# Example usage
user_id = input("Enter your user ID: ")
product_id = input("Enter the product ID you purchased: ")
track_purchase(user_id, product_id)
print("✅ Purchase tracked successfully.")
