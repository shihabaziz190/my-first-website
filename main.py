from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def init_ecommerce_db():
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            product TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/place-order', methods=['POST'])
def place_order():
    name = request.form.get('customer_name')
    phone = request.form.get('customer_phone')
    product = request.form.get('product_name')
    
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (name, phone, product) VALUES (?, ?, ?)', (name, phone, product))
    conn.commit()
    
    cursor.execute('SELECT id, name, phone, product FROM orders ORDER BY id DESC')
    all_orders = cursor.fetchall()
    conn.close()
    
    order_rows = "".join([f"<tr><td style='border:1px solid #ccc; padding:8px;'>{row[0]}</td><td style='border:1px solid #ccc; padding:8px;'>{row[1]}</td><td style='border:1px solid #ccc; padding:8px;'>{row[2]}</td><td style='border:1px solid #ccc; padding:8px;'>{row[3]}</td></tr>" for row in all_orders])
    
    return f"""
    <div style='text-align: center; font-family: Arial; padding: 20px;'>
        <h1 style='color: #27ae60;'>🎉 আপনার অর্ডারটি সফল হয়েছে!</h1>
        <p>ধন্যবাদ <b>{name}</b>, আমরা দ্রুত আপনার সাথে <b>{phone}</b> নম্বরে যোগাযোগ করব।</p>
        
        <h2 style='margin-top: 40px; color: #2c3e50;'>📋 অর্ডার ম্যানেজমেন্ট (Admin View)</h2>
        <table style='margin: 0 auto; border-collapse: collapse; width: 90%; max-width: 600px;'>
            <tr style='background-color: #eee;'>
                <th style='border:1px solid #ccc; padding:8px;'>Order ID</th>
                <th style='border:1px solid #ccc; padding:8px;'>Customer Name</th>
                <th style='border:1px solid #ccc; padding:8px;'>Phone</th>
                <th style='border:1px solid #ccc; padding:8px;'>Product</th>
            </tr>
            {order_rows}
        </table>
        <br><br>
        <a href='/' style='text-decoration: none; background: #3498db; color: white; padding: 10px 20px; border-radius: 5px;'>পণ্য কিনতে ফিরে যান</a>
    </div>
    """
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
