import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_2026')

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    profile_image = db.Column(db.String(200), default='default.png')

with app.app_context():
    db.create_all()

    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    if admin_email and admin_password:
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin = User(
                name='Admin',
                email=admin_email,
                password=generate_password_hash(admin_password),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash('সব ঘর পূরণ করুন!', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('দুইটি পাসওয়ার্ড একই নয়!', 'danger')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে!', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('এই ইমেইল দিয়ে আগে থেকেই অ্যাকাউন্ট আছে!', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role='user'
        )

        db.session.add(new_user)
        db.session.commit()

        flash('রেজিস্ট্রেশন সফল হয়েছে। এখন লগইন করুন।', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            session['name'] = user.name
            session['role'] = user.role
            flash('সফলভাবে লগইন হয়েছে!', 'success')
            return redirect(url_for('home'))

        flash('ইমেইল অথবা পাসওয়ার্ড ভুল!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        flash('প্রোফাইল দেখতে প্রথমে লগইন করুন।', 'warning')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=session['user']).first()

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()

        if new_name:
            user.name = new_name
            session['name'] = new_name

        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"user_{user.id}_{secure_filename(file.filename)}"

                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                    if user.profile_image and user.profile_image != 'default.png':
                        old_path = os.path.join(app.config['UPLOAD_FOLDER'], user.profile_image)
                        if os.path.exists(old_path):
                            os.remove(old_path)

                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    user.profile_image = filename
                else:
                    flash('শুধুমাত্র PNG, JPG, JPEG অথবা GIF ছবি আপলোড করতে পারবেন!', 'danger')
                    return redirect(url_for('profile'))

        db.session.commit()
        flash('প্রোফাইল সফলভাবে আপডেট করা হয়েছে!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/admin')
def admin():
    if 'user' not in session:
        flash('অ্যাডমিন প্যানেল দেখতে লগইন করুন।', 'warning')
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
 return 'আপনার এই পেজ দেখার অনুমতি নেই!', 403



return render_template('admin.html')