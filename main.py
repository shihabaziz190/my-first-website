from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # প্রোডাকশনে শক্তিশালী সিক্রেট কি ব্যবহার করুন

# টেস্টের জন্য হার্ডকোডেড ইউজার ডাটা
USERS = {
    "user@example.com": {"password": "123", "role": "user"},
    "admin@example.com": {"password": "admin123", "role": "admin"}
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = USERS.get(email)
        if user and user['password'] == password:
            session['user'] = email
            session['role'] = user['role']
            flash('সফলভাবে লগইন করেছেন!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash('ইমেইল অথবা পাসওয়ার্ড ভুল!', 'danger')
            
    return render_template('login.html')

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        flash('আপনার এখানে প্রবেশের অনুমতি নেই!', 'danger')
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('লগআউট করা হয়েছে।', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
