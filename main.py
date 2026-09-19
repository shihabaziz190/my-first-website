import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hadi-online-shop-secret-key-2026")

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

db_url = os.environ.get("DATABASE_URL", "sqlite:///shop.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ------------------ MODELS ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")
    profile_image = db.Column(db.String(200), default="default.png")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200), default="default-product.jpg")
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(40), default="Pending")
    payment_method = db.Column(db.String(40), nullable=False)
    shipping_name = db.Column(db.String(120), nullable=False)
    shipping_phone = db.Column(db.String(40), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="orders")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship("Order", backref="items")
    product = db.relationship("Product")

# ------------------ HELPERS ------------------

def get_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]

def save_cart(cart):
    session["cart"] = cart

def cart_count():
    cart = get_cart()
    return sum(int(v.get("quantity", 0)) for v in cart.values())

def cart_total():
    cart = get_cart()
    total = 0.0
    for item_id, item in cart.items():
        product = Product.query.get(int(item_id))
        if product:
            total += product.price * int(item.get("quantity", 1))
    return round(total, 2)

def create_admin_if_missing():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@gmail.com").strip().lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "123456")

    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin_user = User(
            name="Admin",
            email=admin_email,
            password=generate_password_hash(admin_password),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
    else:
        admin.role = "admin"
        admin.password = generate_password_hash(admin_password)
        db.session.commit()

def seed_products():
    if Product.query.count() == 0:
        products = [
            Product(
                name="Smart Watch Pro",
                description="A premium smartwatch with heart rate tracking, fitness modes, GPS, and AMOLED display.",
                category="Electronics",
                price=149.99,
                stock=25,
                image="watch.jpg",
                featured=True
            ),
            Product(
                name="Wireless Earbuds X",
                description="Premium earbuds with noise cancellation, deep bass, and 30-hour battery life.",
                category="Electronics",
                price=89.99,
                stock=30,
                image="earbuds.jpg",
                featured=True
            ),
            Product(
                name="Urban Denim Jacket",
                description="Modern denim jacket for casual daily wear with a relaxed fit and premium finish.",
                category="Clothing",
                price=79.00,
                stock=18,
                image="jacket.jpg",
                featured=True
            ),
            Product(
                name="Classic White Sneakers",
                description="Minimal, comfortable sneakers designed for everyday fashion and movement.",
                category="Clothing",
                price=64.00,
                stock=22,
                image="sneakers.jpg",
                featured=False
            ),
            Product(
                name="Bluetooth Speaker Mini",
                description="Portable speaker with immersive sound, water resistance, and long playback time.",
                category="Electronics",
                price=59.99,
                stock=40,
                image="speaker.jpg",
                featured=False
            ),
            Product(
                name="Casual Hoodie",
                description="Soft, stylish hoodie made for comfort in all seasons.",
                category="Clothing",
                price=48.50,
                stock=35,
                image="hoodie.jpg",
                featured=False
            )
        ]
        db.session.add_all(products)
        db.session.commit()

# ------------------ DB INIT ------------------

with app.app_context():
    db.create_all()
    create_admin_if_missing()
    seed_products()

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    featured_products = Product.query.filter_by(featured=True).all()
    return render_template("index.html", featured_products=featured_products)

@app.route("/products")
def products():
    category = request.args.get("category", "")
    if category:
        items = Product.query.filter(Product.category.ilike(f"%{category}%")).all()
    else:
        items = Product.query.order_by(Product.id.desc()).all()
    return render_template("products.html", products=items, category=category)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    cart = get_cart()
    quantity = int(request.form.get("quantity", 1))
    product = Product.query.get_or_404(product_id)

    if product.stock <= 0:
        flash("এই পণ্যের স্টক শেষ!", "danger")
        return redirect(url_for("product_detail", product_id=product.id))

    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] += quantity
    else:
        cart[str(product_id)] = {"quantity": quantity}

    save_cart(cart)
    flash("কার্টে যোগ করা হয়েছে!", "success")
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = get_cart()
    cart_items = []
    total = 0.0

    for product_id, data in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            qty = max(1, int(data.get("quantity", 1)))
            total += product.price * qty
            cart_items.append({
                "product": product,
                "quantity": qty,
                "line_total": round(product.price * qty, 2)
            })

    return render_template("cart.html", cart_items=cart_items, total=round(total, 2))

@app.route("/update_cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart = get_cart()
    quantity = max(1, int(request.form.get("quantity", 1)))
    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] = quantity
        save_cart(cart)
    flash("কার্ট আপডেট হয়েছে!", "success")
    return redirect(url_for("cart"))

@app.route("/remove_from_cart/<int:product_id>")
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    flash("পন্যটি কার্ট থেকে সরানো হয়েছে!", "success")
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if "user" not in session:
        flash("দয়া করে লগইন করুন।", "warning")
        return redirect(url_for("login"))

    cart = get_cart()
    if not cart:
        flash("কার্ট খালি!", "warning")
        return redirect(url_for("products"))

    if request.method == "POST":
        name = request.form.get("shipping_name", "").strip()
        phone = request.form.get("shipping_phone", "").strip()
        address = request.form.get("shipping_address", "").strip()
        payment_method = request.form.get("payment_method", "COD")

        if not name or not phone or not address:
            flash("সব তথ্য পূরণ করুন!", "danger")
            return redirect(url_for("checkout"))

        order = Order(
            user_id=User.query.filter_by(email=session["user"]).first().id,
            total=cart_total(),
            payment_method=payment_method,
            shipping_name=name,
            shipping_phone=phone,
            shipping_address=address
        )
        db.session.add(order)
        db.session.commit()

        for product_id, data in cart.items():
            product = Product.query.get(int(product_id))
            if product:
                quantity = int(data.get("quantity", 1))
                if quantity > product.stock:
                    quantity = product.stock

                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price=product.price
                )
                db.session.add(item)

                product.stock -= quantity
                db.session.commit()

        session["cart"] = {}
        flash("অর্ডার সফলভাবে তৈরি হয়েছে!", "success")
        return redirect(url_for("order_success", order_id=order.id))

    total = cart_total()
    return render_template("checkout.html", total=total)

@app.route("/order_success/<int:order_id>")
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("order_success.html", order=order)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("সব ঘর পূরণ করুন!", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("দুইটি পাসওয়ার্ড একই নয়!", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে!", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("এই ইমেইল দিয়ে ইতিমধ্যে অ্যাকাউন্ট আছে!", "danger")
            return redirect(url_for("register"))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="user"
        )
        db.session.add(new_user)
        db.session.commit()

        flash("রেজিস্ট্রেশন সফল হয়েছে। লগইন করুন।", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session["user"] = user.email
            session["name"] = user.name
            session["role"] = user.role
            flash("সফলভাবে লগইন হয়েছে!", "success")
            return redirect(url_for("home"))

        flash("ইমেইল অথবা পাসওয়ার্ড ভুল!", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        flash("প্রোফাইল দেখতে লগইন করুন।", "warning")
        return redirect(url_for("login"))

    user = User.query.filter_by(email=session["user"]).first()

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        if new_name:
            user.name = new_name
            session["name"] = new_name

        if "profile_image" in request.files:
            file = request.files["profile_image"]
            if file and file.filename:
                if allowed_file(file.filename):
                    filename = f"user_{user.id}_{secure_filename(file.filename)}"
                    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

                    if user.profile_image and user.profile_image != "default.png":
                        old_path = os.path.join(app.config["UPLOAD_FOLDER"], user.profile_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                    file.save(filepath)
                    user.profile_image = filename
                else:
                    flash("শুধুমাত্র PNG, JPG, JPEG, GIF ছবি আপলোড করুন!", "danger")
                    return redirect(url_for("profile"))

        db.session.commit()
        flash("প্রোফাইল আপডেট হয়েছে!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)

# ------------------ ADMIN ------------------

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "user" not in session:
        flash("অ্যাডমিন প্যানেল দেখতে লগইন করুন।", "warning")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "আপনার এই পেজ দেখার অনুমতি নেই!", 403

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        price = float(request.form.get("price", 0))
        stock = int(request.form.get("stock", 0))
        featured = "featured" in request.form

        image = request.files.get("image")
        image_name = "default-product.jpg"

        if image and image.filename:
            if allowed_file(image.filename):
                image_name = f"product_{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
                os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))
            else:
                flash("শুধুমাত্র PNG, JPG, JPEG, GIF ছবি আপলোড করুন!", "danger")
                return redirect(url_for("admin"))

        if not name or not description or not category:
            flash("পণ্যের সব তথ্য পূরণ করুন!", "danger")
            return redirect(url_for("admin"))

        new_product = Product(
            name=name,
            description=description,
            category=category,
            price=price,
            stock=stock,
            featured=featured,
            image=image_name
        )
        db.session.add(new_product)
        db.session.commit()
        flash("নতুন পণ্য যোগ হয়েছে!", "success")
        return redirect(url_for("admin"))

    products = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("admin.html", products=products, orders=orders)

@app.route("/admin/delete_product/<int:product_id>")
def delete_product(product_id):
    if "user" not in session:
        flash("অ্যাডমিন প্যানেল দেখতে লগইন করুন।", "warning")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "আপনার এই পেজ দেখার অনুমতি নেই!", 403

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("পণ্যটি মুছে দেওয়া হয়েছে!", "success")
    return redirect(url_for("admin"))

@app.route("/admin/update_order_status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    if "user" not in session:
        flash("অ্যাডমিন প্যানেল দেখতে লগইন করুন।", "warning")
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "আপনার এই পেজ দেখার অনুমতি নেই!", 403

    order = Order.query.get_or_404(order_id)
    order.status = request.form.get("status", order.status)
    db.session.commit()
    flash("অর্ডার স্টেটাস আপডেট হয়েছে!", "success")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)