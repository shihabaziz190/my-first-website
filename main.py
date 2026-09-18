import os
import sqlite3
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        return conn

    conn = sqlite3.connect("ecommerce.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if os.environ.get("DATABASE_URL"):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                district_thana TEXT NOT NULL,
                village_market TEXT NOT NULL,
                phone TEXT NOT NULL,
                product TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                district_thana TEXT NOT NULL,
                village_market TEXT NOT NULL,
                phone TEXT NOT NULL,
                product TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    cursor.close()
    conn.close()

def get_all_orders():
    conn = get_db_connection()
    if os.environ.get("DATABASE_URL"):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, district_thana, village_market, phone, product, created_at
            FROM orders
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    else:
        rows = conn.execute("""
            SELECT id, name, district_thana, village_market, phone, product, created_at
            FROM orders
            ORDER BY id DESC
        """).fetchall()
        conn.close()
        return rows

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_panel"))
        return render_template("login.html", error="ভুল username/password")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin_panel():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    orders = get_all_orders()
    return render_template("admin.html", orders=orders)

@app.route("/place-order", methods=["POST"])
def place_order():
    name = request.form.get("customer_name", "").strip()
    district_thana = request.form.get("district_thana", "").strip()
    village_market = request.form.get("village_market", "").strip()
    phone = request.form.get("customer_phone", "").strip()
    product = request.form.get("product_name", "").strip()

    if not name or not district_thana or not village_market or not phone or not product:
        return "সব ফিল্ড পূরণ করুন।", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    if os.environ.get("DATABASE_URL"):
        cursor.execute("""
            INSERT INTO orders (name, district_thana, village_market, phone, product)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, district_thana, village_market, phone, product))
    else:
        cursor.execute("""
            INSERT INTO orders (name, district_thana, village_market, phone, product)
            VALUES (?, ?, ?, ?, ?)
        """, (name, district_thana, village_market, phone, product))

    conn.commit()
    cursor.close()
    conn.close()

    return f"""
    <div style='text-align: center; font-family: Arial; padding: 30px;'>
        <h1 style='color: #27ae60;'>🎉 আপনার অর্ডারটি সফল হয়েছে!</h1>
        <p>ধন্যবাদ <b>{name}</b>। আমরা দ্রুত আপনার সাথে <b>{phone}</b> নম্বরে যোগাযোগ করব।</p>
        <br>
        <a href='/' style='text-decoration: none; background: #3498db; color: white; padding: 10px 20px; border-radius: 5px; display: inline-block;'>পণ্য কিনতে ফিরে যান</a>
    </div>
    """

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
