from flask import Flask, render_template, request

app = Flask(__name__)

# মূল হোম পেজ দেখানোর লজিক
@app.route('/')
def home():
    return render_template('index.html')

# বাটনে ক্লিক করলে কি কাজ হবে তার লজিক
@app.route('/submit', methods=['POST'])
def submit():
    user_name = request.form.get('username')
    return f"<h1 style='color: green; text-align: center; margin-top: 50px;'>ধন্যবাদ, {user_name}!</h1><p style='text-align: center;'>Flask আপনার ইনপুটটি সফলভাবে প্রসেস করেছে।</p><br><center><a href='/'>আবার চেষ্টা করুন</a></center>"

if __name__ == '__main__':
    app.run(debug=True)
