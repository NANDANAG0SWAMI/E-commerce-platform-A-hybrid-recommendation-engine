import firebase_admin
from firebase_admin import credentials, firestore
import requests
import os

# Load Firebase credentials
cred_path = os.getenv("FIREBASE_CREDENTIAL_PATH")
if not cred_path:
    raise ValueError("FIREBASE_CREDENTIAL_PATH not set.")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()

# Fetch product data
response = requests.get("https://dummyjson.com/products?limit=100")
products = response.json().get("products", [])

# Upload each product to Firestore
for product in products:
    product_id = str(product["id"])
    db.collection("products").document(product_id).set(product)

print("✅ Products uploaded to Firestore!")
