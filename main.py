import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'hadi-ecommerce-secret-key-2026')

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///shop.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(60), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='Pending')
    payment = db.Column(db.String(30), nullable=False)
    customer = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), nullable=False)
    address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User')


def cart_dict():
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']


def cart_total():
    total = 0.0
    for product_id, qty in cart_dict().items():
        product = Product.query.get(int(product_id))
        if product:
            total += product.price * int(qty)
    return round(total, 2)


@app.context_processor
def inject_globals():
    return {'cart_count': lambda: sum(int(v) for v in cart_dict().values())}


def is_admin():
    return session.get('role') == 'admin'


def seed_products():
    if Product.query.count() == 0:
        products = [
            Product(name='Smart Watch Pro', description='Premium smartwatch for daily fitness tracking and notification alerts.', category='Electronics', price=149.99, stock=12),
            Product(name='Wireless Earbuds X', description='Crisp sound, noise cancellation, and long battery life.', category='Electronics', price=89.99, stock=18),
            Product(name='Urban Denim Jacket', description='Modern casual jacket for all-day comfort and style.', category='Clothing', price=79.00, stock=9),
            Product(name='Classic White Sneakers', description='Lightweight everyday sneakers built for comfort.', category='Clothing', price=64.00, stock=15),
            Product(name='Bluetooth Speaker Mini', description='Portable speaker with rich bass and compact size.', category='Electronics', price=59.99, stock=20),
            Product(name='Casual Hoodie', description='Soft and stylish hoodie for daily wear.', category='Clothing', price=48.50, stock=25),
        ]
        db.session.add_all(products)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_products()

    admin_email = os.getenv('ADMIN_EMAIL', 'admin@gmail.com').lower().strip()
    admin_password = os.getenv('ADMIN_PASSWORD', '123456')
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        db.session.add(User(
            name='Admin',
            email=admin_email,
            password=generate_password_hash(admin_password),
            role='admin'
        ))
        db.session.commit()


@app.route('/')
def home():
    products = Product.query.order_by(Product.id.desc()).limit(6).all()
    return render_template('index.html', products=products)


@app.route('/products')
def products():
    category = request.args.get('category', '').strip()
    if category:
        items = Product.query.filter_by(category=category).order_by(Product.id.desc()).all()
    else:
        items = Product.query.order_by(Product.id.desc()).all()
    return render_template('products.html', products=items, category=category)


@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)


@app.route('/cart')
def cart_page():
    items = []
    for product_id, qty in cart_dict().items():
        product = Product.query.get(int(product_id))
        if product:
            items.append((product, int(qty)))
    return render_template('cart.html', items=items, total=cart_total())


@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    qty = max(1, int(request.form.get('quantity', 1)))
    cart = cart_dict()
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    session.modified = True
    flash('কার্টে পণ্য যোগ হয়েছে!', 'success')
    return redirect(url_for('cart_page'))


@app.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    cart = cart_dict()
    cart.pop(str(product_id), None)
    session.modified = True
    flash('পণ্যটি কার্ট থেকে সরানো হয়েছে!', 'success')
    return redirect(url_for('cart_page'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user' not in session:
        flash('চেকআউট করতে লগইন করুন।', 'warning')
        return redirect(url_for('login'))

    if not cart_dict():
        flash('কার্ট খালি!', 'warning')
        return redirect(url_for('products'))

    if request.method == 'POST':
        customer = request.form.get('customer', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        payment = request.form.get('payment', 'COD')

        if not customer or not phone or not address:
            flash('সব তথ্য পূরণ করুন!', 'danger')
            return redirect(url_for('checkout'))

        user = User.query.filter_by(email=session['user']).first()
        order = Order(
            user_id=user.id,
            total=cart_total(),
            payment=payment,
            customer=customer,
            phone=phone,
            address=address,
        )
        db.session.add(order)
        db.session.commit()

        for product_id, qty in list(cart_dict().items()):
            product = Product.query.get(int(product_id))
            if product:
                product.stock = max(0, product.stock - int(qty))
        db.session.commit()

        session['cart'] = {}
        return render_template('success.html', order=order)

    return render_template('checkout.html', total=cart_total())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('সব ঘর পূরণ করুন!', 'danger')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে!', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('এই ইমেইল দিয়ে অ্যাকাউন্ট আছে!', 'danger')
            return redirect(url_for('register'))

        user = User(name=name, email=email, password=generate_password_hash(password), role='user')
        db.session.add(user)
        db.session.commit()
        flash('রেজিস্ট্রেশন সফল হয়েছে। লগইন করুন!', 'success')
        return redirect(url_for('login'))

    return render_template('auth.html', register=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            session['role'] = user.role
            flash('সফলভাবে লগইন হয়েছে!', 'success')
            return redirect(url_for('home'))

        flash('ইমেইল বা পাসওয়ার্ড ভুল!', 'danger')

    return render_template('auth.html', register=False)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if 'user' not in session:
        flash('অ্যাডমিন প্যানেল দেখতে লগইন করুন।', 'warning')
        return redirect(url_for('login'))
    if not is_admin():
        return 'আপনি এই পেজ দেখতে পারবেন না!', 403

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))

        if not name or not description or not category:
            flash('সব তথ্য পূরণ করুন!', 'danger')
            return redirect(url_for('admin_panel'))

        db.session.add(Product(
            name=name,
            description=description,
            category=category,
            price=price,
            stock=stock,
        ))
        db.session.commit()
        flash('নতুন পণ্য যোগ হয়েছে!', 'success')
        return redirect(url_for('admin_panel'))

    products = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('admin.html', products=products, orders=orders)


@app.route('/admin/delete/<int:product_id>')
def delete_product(product_id):
    if 'user' not in session or not is_admin():
        return 'অ্যাডমিন ছাড়া অনুমতি নেই!', 403
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('পণ্যটি মুছে দেওয়া হয়েছে!', 'success')
    return redirect(url_for('admin_panel'))


@app.route('/admin/order/<int:order_id>', methods=['POST'])
def update_order(order_id):
    if 'user' not in session or not is_admin():
        return 'অ্যাডমিন ছাড়া অনুমতি নেই!', 403
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get('status', order.status)
    db.session.commit()
    flash('অর্ডার স্ট্যাটাস আপডেট হয়েছে!', 'success')
    return redirect(url_for('admin_panel'))


if __name__ == '__main__':
    app.run(debug=True)