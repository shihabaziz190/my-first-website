import os
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@gmail.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "123456")
SECRET_KEY = os.environ.get("SECRET_KEY", "temporary-secret-key")
app.secret_key = SECRET_KEY

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_in_production'

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "123456"

USERS = {
    ADMIN_EMAIL: {
        "password": ADMIN_PASSWORD,
        "role": "admin"
    }
}

# Mock Database
PRODUCTS = [
    {"id": 1, "name": "Minimalist Watch", "price": 120.0, "category": "Accessories", "image": "https://via.placeholder.com/300", "description": "Sleek and classic wristwatch."},
    {"id": 2, "name": "Wireless Headphones", "price": 199.99, "category": "Electronics", "image": "https://via.placeholder.com/300", "description": "High-fidelity sound cancellation."},
    {"id": 3, "name": "Leather Backpack", "price": 85.0, "category": "Bags", "image": "https://via.placeholder.com/300", "description": "Durable handcrafted genuine leather."},
]


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') != ADMIN_EMAIL:
            flash("Admin access required.", "danger")
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_cart_count():
    cart = session.get('cart', {})
    count = sum(cart.values())
    return dict(cart_count=count)


@app.route('/')
def index():
    featured = PRODUCTS[:2]
    return render_template('index.html', products=featured)


@app.route('/products')
def products():
    category = request.args.get('category')
    if category:
        filtered = [p for p in PRODUCTS if p['category'].lower() == category.lower()]
    else:
        filtered = PRODUCTS
    return render_template('products.html', products=filtered)


@app.route('/product/<int:product_id>')
def product(product_id):
    item = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not item:
        flash("Product not found", "warning")
        return redirect(url_for('products'))
    return render_template('product.html', product=item)


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = session.get('cart', {})
    str_id = str(product_id)
    cart[str_id] = cart.get(str_id, 0) + int(request.form.get('quantity', 1))
    session['cart'] = cart
    flash("Item added to cart!", "success")
    return redirect(url_for('cart'))


@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0.0
    for str_id, qty in cart.items():
        item = next((p for p in PRODUCTS if p['id'] == int(str_id)), None)
        if item:
            subtotal = item['price'] * qty
            total += subtotal
            cart_items.append({'product': item, 'qty': qty, 'subtotal': subtotal})
    return render_template('cart.html', items=cart_items, total=total)


@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', {})
    for key, val in request.form.items():
        if key.startswith('qty_'):
            prod_id = key.split('_')[1]
            qty = int(val)
            if qty > 0:
                cart[prod_id] = qty
            else:
                cart.pop(prod_id, None)
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        session['cart'] = {}
        return redirect(url_for('success'))
    cart = session.get('cart', {})
    total = sum(next(p['price'] for p in PRODUCTS if p['id'] == int(pid)) * qty for pid, qty in cart.items())
    return render_template('checkout.html', total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        trxid = request.form.get('trxid')
        session['cart'] = {}
        flash(f"Order placed successfully via {payment_method}", "success")
        return redirect(url_for('success'))
    cart = session.get('cart', {})
    total = sum(next(p['price'] for p in PRODUCTS if p['id'] == int(pid)) * qty for pid, qty in cart.items())
    return render_template('checkout.html', total=total)
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = USERS.get(email)
        if user and user['password'] == password:
            session['user'] = email
            flash("Successfully logged in!", "success")
            return redirect(url_for('admin') if user['role'] == 'admin' else url_for('index'))
        flash("Invalid credentials.", "danger")
    return render_template('auth.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('index'))


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    if request.method == 'POST':
        new_id = len(PRODUCTS) + 1
        PRODUCTS.append({
            "id": new_id,
            "name": request.form.get('name'),
            "price": float(request.form.get('price')),
            "category": request.form.get('category'),
            "image": request.form.get('image') or "https://via.placeholder.com/300",
            "description": request.form.get('description')
        })
        flash("Product added successfully!", "success")
        return redirect(url_for('admin'))
    return render_template('admin.html', products=PRODUCTS)


if __name__ == '__main__':
    app.run(debug=True)