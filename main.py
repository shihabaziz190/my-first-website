import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_2026')

# ------------------------------------
# UPLOAD CONFIGURATION
# ------------------------------------
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# সর্বোচ্চ ফাইল সাইজ: 2MB
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------------------
# DATABASE CONFIGURATION
# ------------------------------------
db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------------
# Database Model
# ------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    profile_image = db.Column(db.String(200), default='default.png') # প্রোফাইল ছবি নাম

# ------------------------------------
# Profile & Image Upload Routes
# ------------------------------------

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        flash('প্রোফাইল দেখতে প্রথমে লগইন করুন।', 'warning')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=session['user']).first()

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        
        # ১. নাম আপডেট
        if new_name:
            user.name = new_name
            session['name'] = new_name

        # ২. প্রোফাইল ছবি আপলোড প্রসেসিং
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    # ইউনিক ফাইলের নাম তৈরি (ইউজার আইডি দিয়ে)
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"user_{user.id}_{secure_filename(file.filename)}"
                    
                    # static/uploads ফোল্ডার না থাকলে তৈরি করা
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    
                    # পুরাতন ছবি মুছে ফেলা (যদি ডিফল্ট ছবি না হয়ে থাকে)
                    if user.profile_image and user.profile_image != 'default.png':
                        old_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    # ডাটাবেসে নতুন ছবির ফাইল নেম সেভ করা
                    user.profile_image = filename
                else:
                    flash('শুধুমাত্র PNG, JPG, JPEG অথবা GIF ছবি আপলোড করতে পারবেন!', 'danger')
                    return redirect(url_for('profile'))

        db.session.commit()
        flash('প্রোফাইল সফলভাবে আপডেট করা হয়েছে!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            session['name'] = user.name
            session['role'] = user.role
            return redirect(url_for('home'))

        flash('ইমেইল অথবা পাসওয়ার্ড ভুল!', 'danger')

    return render_template('login.html')
with app.app_context():
    db.create_all()
with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@gmail.com').first():
        user = User(
            name='Admin',
            email='admin@gmail.com',
            password=generate_password_hash('123456'),
            role='admin'
        )
        db.session.add(user)
        db.session.commit()