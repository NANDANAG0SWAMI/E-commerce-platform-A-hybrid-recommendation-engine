Hybrid Recommendation System POC

A Flask-based e-commerce proof-of-concept that demonstrates various product recommendation algorithms. This application simulates a retail environment to track user behavior and serve personalized content using a hybrid approach of collaborative filtering and rule-based logic.


🚀 Features:
User Authentication: Login and Registration system with session management.
Product Catalog: Fetches real-time product data from dummyjson.com.
Shopping Cart: Full cart functionality (Add, Remove, Checkout).
Activity Tracking: Logs user views, cart additions, and purchases to both local JSON storage and Firebase Firestore.
Recommendation Engines:
   🏆 Bestsellers: Top-selling items based on purchase history.
   📈 Trending: Items with high recent activity.
   🤝 Bought Together: Association rule mining for complementary products.
   🎯 Personalized: Suggestions based on specific user history.
   👀 Recently Viewed: User's navigation history.
   🔄 Similar Items: Collaborative filtering (Users who bought X also bought Y).
Visual AI Experiment: Includes a script (ECS_API_IMG.py) utilizing Groq/Llama for image content analysis.


📂 Project Structure
1. app.py / dup.py: Main Flask application entry points. Handles routing, auth, and UI rendering.
2. generate_dummy_data.py: Python script to generate synthetic sales, views, and transaction history to "cold start" the recommendation engine.
3. store_products.py: Fetches products from the external API and seeds the Firebase Firestore database.
4. track_views.py / view_purchases.py: Utility scripts for testing database logging independently of the web UI.
5. algorithms/: (Expected folder) Contains the logic for the recommendation engines (trending, bestsellers, etc.).
6. data/: Stores local JSON logs (sales.json, views.json, transactions.json).


🛠️ Prerequisites
1. Python 3.8+
2. A Firebase Service Account Key (JSON)
3. Groq API Key (Optional, for image analysis)

📦 Installation
1. Clone the repository:
       git clone <repository-url>
       cd Recommendation_poc
2. Install dependencies:
       pip install flask firebase-admin requests
3. Configuration:
       i. Place your Firebase Service Account Key in the root directory.
       ii. Note: Ensure your key filename matches the path in app.py (currently set to firebase_hybrec_new_key.json) or update the code variable cred_path.


⚙️ Setup & Usage
1. Generate Data
      Before running the app, generate dummy data so the recommendation algorithms have something to work with:
            python generate_dummy_data.py
2. Seed Database (Optional)
      If you want to populate your Firebase instance with the product catalog:
            python store_products.py
3. Run the Application
      Start the Flask server:
            python app.py
Access the application in your browser at: http://127.0.0.1:5000


🛡️ Security Note
Create a .gitignore file: Ensure you do not commit your API keys or private JSON credentials. Create a .gitignore file in the root directory containing:
__pycache__/
*.json
*.csv
venv/


🧪 API Endpoints
The application exposes several internal API endpoints for fetching recommendations:
/api/bestsellers
/api/trending
/api/bought_together
/api/personalized
/api/recently_viewed
