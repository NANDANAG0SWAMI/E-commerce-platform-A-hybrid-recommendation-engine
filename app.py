from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
import json, os, requests
from datetime import datetime
from functools import wraps
import sys
import csv
sys.path.append(r'C:/Users/nanda/OneDrive/Desktop/Recommendation_poc/algorithms')
from algorithms.trending import get_trending_products
from algorithms.bestsellers import get_bestsellers
from algorithms.recent_views import get_recent_views
from algorithms.bought_together import get_frequent_pairs
from algorithms.others_viewed import get_similar_items
from algorithms.personalized import get_personalized_picks


app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['TEMPLATES_AUTO_RELOAD'] = True

USERS_FILE = 'dummy_users_400_final.csv'
SALES_FILE = 'sales.json'
VIEWS_FILE = 'views.json'
TRANSACTIONS_FILE = 'transactions.json'

def convert_csv_to_json(csv_file, json_file):
    users = {}
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            username = row['username']  # adjust column name as needed
            password = row['password']  # adjust column name as needed
            users[username] = {'password': password}
    
    with open(json_file, 'w') as f:
        json.dump(users, f, indent=2)

# Run once:
convert_csv_to_json('dummy_users_400_final.csv', 'users.json')

# Initialize files
for file in [USERS_FILE, SALES_FILE, VIEWS_FILE, TRANSACTIONS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

def load_json(file):
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

@app.context_processor
def utility_processor():
    def get_cart_count():
        if 'user' in session:
            carts = load_json(VIEWS_FILE)
            return len(carts.get(session['user'], []))
        return 0
    return dict(get_cart_count=get_cart_count)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper



    query = request.args.get('q', '').strip().lower()
    if query:
        bestsellers = [p for p in bestsellers if query in p['title'].lower()]

    return render_template_string(PAGE_TEMPLATE, username=username, products=bestsellers, search_query=query)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        users = load_json(USERS_FILE)
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('index'))
        error = "Invalid credentials"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        users = load_json(USERS_FILE)
        username = request.form['username']
        password = request.form['password']
        if len(username) < 4 or len(password) < 6:
            error = "Username must be at least 4 characters and password 6 characters"
        elif username in users:
            error = "User already exists"
        else:
            users[username] = {'password': password}
            save_json(USERS_FILE, users)
            return redirect(url_for('login'))
    return render_template_string(REGISTER_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/log_activity', methods=['POST'])
@login_required
def log_activity():
    data = request.json
    username = session['user']
    activity = load_json(SALES_FILE)
    
    if username not in activity:
        activity[username] = []
        
    activity[username].append({
        'product_id': data['product_id'],
        'action': data['action'],
        'timestamp': datetime.utcnow().isoformat()
    })
    
    if data['action'] == 'add_to_cart':
        carts = load_json(VIEWS_FILE)
        if username not in carts:
            carts[username] = []
            
        if data['product_id'] not in [item['product_id'] for item in carts[username]]:
            product = next((p for p in load_products() if p['id'] == data['product_id']), None)
            if product:
                carts[username].append({
                    'product_id': product['id'],
                    'title': product['title'],
                    'price': product['price'],
                    'quantity': 1,
                    'added_at': datetime.utcnow().isoformat()
                })
                save_json(VIEWS_FILE, carts)
    
    if data['action'] == 'purchase':
        purchases = load_json(TRANSACTIONS_FILE)
        if username not in purchases:
            purchases[username] = []
            
        purchases[username].append({
            'product_id': data['product_id'],
            'purchased_at': datetime.utcnow().isoformat()
        })
        save_json(TRANSACTIONS_FILE, purchases)
    
    save_json(SALES_FILE, activity)
    return jsonify(status='ok')

@app.route('/cart')
@login_required
def cart():
    username = session['user']
    carts = load_json(VIEWS_FILE)
    user_cart = carts.get(username, [])
    return render_template_string(CART_TEMPLATE, cart_items=user_cart)

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    username = session['user']
    carts = load_json(VIEWS_FILE)
    
    if username in carts:
        carts[username] = [item for item in carts[username] if item['product_id'] != product_id]
        save_json(VIEWS_FILE, carts)
    
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    username = session['user']
    carts = load_json(VIEWS_FILE) 
    purchases = load_json(TRANSACTIONS_FILE)
    
    if username in carts and len(carts[username]) > 0:
        for item in carts[username]:
            requests.post('http://localhost:5000/log_activity', 
                json={'product_id': item['product_id'], 'action': 'purchase'})
        
        if username not in purchases:
            purchases[username] = []
        purchases[username].extend(carts[username])
        save_json(TRANSACTIONS_FILE, purchases)
        
        carts[username] = []
        save_json(VIEWS_FILE, carts)
    
    return redirect(url_for('cart'))

def load_products():
    try:
        response = requests.get("https://dummyjson.com/products?limit=500")
        return response.json().get('products', [])
    except:
        return []
    
@app.route('/')
@login_required
def index():
    username = session['user']
    all_products = load_products()

    query = request.args.get('q', '').strip().lower()
    if query:
        all_products = [p for p in all_products if query in p['title'].lower()]

    return render_template_string(PAGE_TEMPLATE, username=username, products=all_products, search_query=query)

@app.route('/bestsellers')
@login_required
def bestsellers():
    products = load_products()
    top_ids = get_bestsellers(SALES_FILE)
    filtered = [p for p in products if p['id'] in top_ids]
    return render_template_string(PAGE_TEMPLATE, username=session['user'], products=filtered)

@app.route('/bought_together')
@login_required
def bought_together():
    products = load_products()
    top_ids = get_frequent_pairs(SALES_FILE)
    filtered = [p for p in products if p['id'] in top_ids]
    return render_template_string(PAGE_TEMPLATE, username=session['user'], products=filtered)

@app.route('/others_viewed')
@login_required
def others_viewed():
    products = load_products()
    top_ids = get_similar_items(SALES_FILE)
    filtered = [p for p in products if p['id'] in top_ids]
    return render_template_string(PAGE_TEMPLATE, username=session['user'], products=filtered)

@app.route('/personalized')
@login_required
def personalized():
    products = load_products()
    top_ids = get_personalized_picks(session['user'], SALES_FILE)
    filtered = [p for p in products if p['id'] in top_ids]
    return render_template_string(PAGE_TEMPLATE, username=session['user'], products=filtered)

@app.route('/recently_viewed')
@login_required
def recently_viewed():
    products = load_products()
    top_ids = get_recent_views(session['user'], SALES_FILE)
    filtered = [p for p in products if p['id'] in top_ids]
    return render_template_string(PAGE_TEMPLATE, username=session['user'], products=filtered)

@app.route('/trending')
@login_required
def trending():
    products = load_products()
    top_ids = get_trending_products(SALES_FILE)
    filtered = [p for p in products if p['id'] in top_ids]
    return render_template_string(PAGE_TEMPLATE, username=session['user'], products=filtered)


# HTML Templates with Bootstrap
BASE_STYLES = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    .product-card { transition: transform 0.2s, box-shadow 0.2s; }
    .product-card:hover { 
        transform: translateY(-5px); 
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        cursor: pointer;
    }
    .product-image { height: 200px; object-fit: cover; }
    .cart-badge { position: relative; }
    .badge-notification { position: absolute; top: -5px; right: -5px; }
</style>
"""

LOGIN_TEMPLATE = BASE_STYLES + """
<div class="container mt-5" style="max-width: 400px;">
    <div class="card shadow">
        <div class="card-body">
            <h2 class="card-title text-center mb-4">Login</h2>
            {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
            {% endif %}
            <form method="post">
                <div class="mb-3">
                    <input type="text" class="form-control" name="username" placeholder="Username" required>
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
            </form>
            <div class="text-center mt-3">
                <a href="{{ url_for('register') }}" class="text-decoration-none">Create an account</a>
            </div>
        </div>
    </div>
</div>
"""

REGISTER_TEMPLATE = BASE_STYLES + """
<div class="container mt-5" style="max-width: 400px;">
    <div class="card shadow">
        <div class="card-body">
            <h2 class="card-title text-center mb-4">Register</h2>
            {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
            {% endif %}
            <form method="post">
                <div class="mb-3">
                    <input type="text" class="form-control" name="username" placeholder="Username" required>
                </div>
                <div class="mb-3">
                    <input type="password" class="form-control" name="password" placeholder="Password" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Register</button>
            </form>
            <div class="text-center mt-3">
                <a href="{{ url_for('login') }}" class="text-decoration-none">Already have an account?</a>
            </div>
        </div>
    </div>
</div>
"""

PAGE_TEMPLATE = BASE_STYLES + """
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
    <div class="container">
        <a class="navbar-brand" href="{{ url_for('index') }}">Product Store</a>
        <div class="d-flex align-items-center">
           <form class="d-flex me-3" method="get" action="{{ url_for('index') }}">
        <input class="form-control me-2" type="search" name="q" placeholder="Search products..." value="{{ search_query or '' }}">
        <button class="btn btn-light" type="submit">Search</button>
    </form>
            <span class="text-white me-3">Hello, {{ username }}</span>
            <a href="{{ url_for('cart') }}" class="btn btn-outline-light position-relative me-2">
                <i class="fas fa-shopping-cart"></i>
                <span class="badge bg-danger badge-notification">
                    {{ get_cart_count() }}
                </span>
            </a>
            <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Logout</a>
        </div>
    </div>
</nav>

<!-- Darker Blue Ribbon Menu -->
<div class="bg-dark text-white py-2">
    <div class="container d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center">
            <button class="btn btn-dark me-3" onclick="toggleSidebar()">
                <i class="fas fa-bars"></i>
            </button>
            <strong class="me-2"></strong>
            <div id="categoryMenu" class="d-none d-md-flex flex-wrap gap-3">
                <a href="#" class="text-white text-decoration-none">Electronics</a>
                <a href="#" class="text-white text-decoration-none">Fashion</a>
                <a href="#" class="text-white text-decoration-none">Groceries</a>
                <a href="#" class="text-white text-decoration-none">Home</a>
                <a href="#" class="text-white text-decoration-none">Books</a>
                <a href="#" class="text-white text-decoration-none">Help</a>
            </div>
        </div>
    </div>
</div>

<!-- Sidebar (Offcanvas Style) -->
<div id="sidebarMenu" class="bg-dark text-white position-fixed top-0 start-0 vh-100 p-4 shadow-lg d-none" style="width: 250px; z-index: 1050;">
  <div class="d-flex align-items-center justify-content-start mb-4">
    <button onclick="toggleSidebar()" class="btn btn-sm btn-outline-light me-2">
        <i class="fas fa-arrow-left"></i>
    </button>
    <h5 class="m-0">Menu</h5>
</div>
    <ul class="nav flex-column gap-2">
        <li><a href="{{ url_for('index') }}" class="text-white text-decoration-none">🏆 Best Sellers</a></li>
        <li><a href="#" class="text-white text-decoration-none">🤝 Bought Together</a></li>
        <li><a href="#" class="text-white text-decoration-none">👀 Others Viewed</a></li>
        <li><a href="#" class="text-white text-decoration-none">🎯 Personalized</a></li>
        <li><a href="#" class="text-white text-decoration-none">🕒 Recently Viewed</a></li>
        <li><a href="#" class="text-white text-decoration-none">📈 Trending</a></li>
    </ul>
</div>

<div class="container">
    <div class="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4">
    {% if products|length == 0 %}
    <div class="alert alert-warning">No products match your search.</div>
{% endif %}
        {% for p in products %}
        <div class="col">
            <div class="card product-card h-100" data-bs-toggle="modal" data-bs-target="#productModal" 
                 onclick="showProductDetails({{ p['id'] }})">
                <img src="{{ p['thumbnail'] }}" class="card-img-top product-image">
                <div class="card-body">
                    <h5 class="card-title">{{ p['title'] }}</h5>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="badge bg-success">${{ p['price'] }}</span>
                        <span class="badge bg-warning text-dark">⭐ {{ p['rating'] }}</span>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<!-- Product Modal -->
<div class="modal fade" id="productModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="productTitle"></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <img id="productImage" class="img-fluid mb-3">
                <p id="productDescription"></p>
                <div class="d-flex justify-content-between mb-3">
                    <span class="badge bg-success" id="productPrice"></span>
                    <span class="badge bg-warning text-dark" id="productRating"></span>
                </div>
                <div class="d-grid gap-2">
                    <button class="btn btn-primary" onclick="addToCart()">
                        <i class="fas fa-cart-plus"></i> Add to Cart
                    </button>
                    <button class="btn btn-success" onclick="buyNow()">
                        <i class="fas fa-bolt"></i> Buy Now
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let currentProductId = null;

function showProductDetails(productId) {
    currentProductId = productId;
    fetch('https://dummyjson.com/products/' + productId)
        .then(res => res.json())
        .then(product => {
            document.getElementById('productTitle').textContent = product.title;
            document.getElementById('productImage').src = product.thumbnail;
            document.getElementById('productDescription').textContent = product.description;
            document.getElementById('productPrice').textContent = '$' + product.price;
            document.getElementById('productRating').textContent = '⭐ ' + product.rating;
        });
}

function addToCart() {
    fetch('/log_activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: currentProductId, action: 'add_to_cart' })
    }).then(() => location.reload());
}

function buyNow() {
    fetch('/log_activity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: currentProductId, action: 'purchase' })
    }).then(() => {
        alert('Purchase successful!');
        location.reload();
    });
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebarMenu');
    sidebar.classList.toggle('d-none');
}

</script>
"""


CART_TEMPLATE = BASE_STYLES + """
<nav class="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
    <div class="container">
        <a class="navbar-brand" href="{{ url_for('index') }}">Product Store</a>
        <div class="d-flex align-items-center">
            <span class="text-white me-3">Hello, {{ session['user'] }}</span>
            <a href="{{ url_for('index') }}" class="btn btn-outline-light me-2">Continue Shopping</a>
            <a href="{{ url_for('logout') }}" class="btn btn-outline-light">Logout</a>
        </div>
    </div>
</nav>

<div class="container">
    <h3 class="mb-4">Your Cart</h3>
    {% if cart_items %}
    <div class="row g-4">
        {% for item in cart_items %}
        <div class="col-12">
            <div class="card shadow-sm">
                <div class="row g-0">
                    <div class="col-md-2">
                        <img src="https://dummyjson.com/image/80x80/ced4da/fff?text=Product" 
                             class="img-fluid rounded-start" alt="{{ item.title }}">
                    </div>
                    <div class="col-md-8">
                        <div class="card-body">
                            <h5 class="card-title">{{ item.title }}</h5>
                            <p class="card-text">${{ item.price }}</p>
                        </div>
                    </div>
                    <div class="col-md-2 d-flex align-items-center justify-content-end">
                        <a href="/remove_from_cart/{{ item.product_id }}" class="btn btn-danger">
                            <i class="fas fa-trash"></i>
                        </a>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    <div class="mt-4 text-end">
        <h4>Total: ${{ cart_items|sum(attribute='price') }}</h4>
        <a href="{{ url_for('checkout') }}" class="btn btn-success btn-lg">
            <i class="fas fa-shopping-bag"></i> Checkout
        </a>
    </div>
    {% else %}
    <div class="alert alert-info">Your cart is empty</div>
    {% endif %}
</div>
"""

if __name__ == '__main__':
    app.run(debug=True)