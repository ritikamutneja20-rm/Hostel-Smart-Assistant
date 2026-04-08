from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    # Users
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        password TEXT
    )
    ''')

    # Complaints
    cur.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        complaint TEXT,
        status TEXT
    )
    ''')

    # Leaves
    cur.execute('''
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        reason TEXT,
        status TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return render_template('welcome.html')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/register')
def register_page():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
    conn.commit()
    conn.close()

    return redirect('/login')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Admin
    if email == "admin@123" and password == "admin":
        return redirect('/admin')

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()
    conn.close()

    if user:
        session['user'] = email
        return redirect('/dashboard')
    else:
        return "Invalid Login ❌"


# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')


# ---------------- COMPLAINT ----------------

@app.route('/submit_complaint', methods=['POST'])
def submit_complaint():
    email = session.get('user')
    complaint = request.form['complaint']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO complaints (email, complaint, status) VALUES (?, ?, ?)",
                (email, complaint, "Pending"))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/view_complaints')
def view_complaints():
    email = session.get('user')

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT complaint, status FROM complaints WHERE email=?", (email,))
    data = cur.fetchall()
    conn.close()

    return render_template('view.html', data=data)


# ---------------- LEAVE ----------------

@app.route('/leave')
def leave():
    return render_template('leave.html')


@app.route('/apply_leave', methods=['POST'])
def apply_leave():
    email = session.get('user')
    reason = request.form['reason']

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO leave_requests (email, reason, status) VALUES (?, ?, ?)",
                (email, reason, "Pending"))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/my_leaves')
def my_leaves():
    email = session.get('user')

    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT reason, status FROM leave_requests WHERE email=?", (email,))
    data = cur.fetchall()
    conn.close()

    return render_template('my_leave.html', data=data)


# ---------------- OTHER ----------------

@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/bill')
def bill():
    return render_template('bill.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/help')
def help():
    return render_template('help.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- ADMIN ----------------

@app.route('/admin')
def admin():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT id, email, complaint, status FROM complaints")
    data = cur.fetchall()
    conn.close()

    return render_template('admin.html', data=data)


@app.route('/update/<int:id>')
def update(id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("UPDATE complaints SET status='Resolved' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin')


# 🔥 ADMIN LEAVES

@app.route('/admin_leaves')
def admin_leaves():
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("SELECT id, email, reason, status FROM leave_requests")
    data = cur.fetchall()
    conn.close()

    return render_template('admin_leave.html', data=data)


@app.route('/approve_leave/<int:id>')
def approve_leave(id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("UPDATE leave_requests SET status='Approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin_leaves')


@app.route('/reject_leave/<int:id>')
def reject_leave(id):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute("UPDATE leave_requests SET status='Rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/admin_leaves')


# ---------------- RUN ----------------

if __name__ == '__main__':
    app.run(debug=True)