from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import functools
import random

DB = 'app.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password_hash TEXT,
        transaction_limit REAL,
        last_location TEXT,
        avg_amount REAL DEFAULT 0,
        tx_count INTEGER DEFAULT 0
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        location TEXT,
        timestamp TEXT,
        status TEXT,
        reason TEXT
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS otps (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        code TEXT,
        expires_at TEXT
    )
    ''')
    # ensure reason column exists (for older DBs)
    try:
        c.execute("ALTER TABLE transactions ADD COLUMN reason TEXT")
    except sqlite3.OperationalError:
        # column probably exists
        pass
    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = 'change-this-in-production'
app.permanent_session_lifetime = timedelta(minutes=30)

def get_db_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database at startup

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    conn = get_db_conn()
    user = conn.execute('SELECT * FROM users WHERE id=?', (uid,)).fetchone()
    conn.close()
    return user

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access that page', 'danger')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped_view

@app.route('/')
def index():
    user = current_user()
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('register.html')
        limit = float(request.form.get('limit', '1000'))
        location = request.form.get('location', '')
        pw_hash = generate_password_hash(password)
        conn = get_db_conn()
        try:
            conn.execute('INSERT INTO users (username,password_hash,transaction_limit,last_location) VALUES (?,?,?,?)',
                         (username, pw_hash, limit, location))
            conn.commit()
            flash('Registered successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_conn()
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user_id'] = user['id']
            flash('Logged in', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    conn = get_db_conn()
    txs = conn.execute('SELECT * FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10', (user['id'],)).fetchall()
    conn.close()
    return render_template('dashboard.html', user=user, transactions=txs)


@app.route('/admin')
@login_required
def admin():
    user = current_user()
    # simple admin check: username == 'admin'
    if not user or user['username'] != 'admin':
        flash('Admin access required', 'danger')
        return redirect(url_for('dashboard'))
    conn = get_db_conn()
    users = conn.execute('SELECT id,username,transaction_limit,avg_amount,tx_count FROM users').fetchall()
    txs = conn.execute('SELECT t.id,t.user_id,t.amount,t.location,t.timestamp,t.status,t.reason,u.username FROM transactions t LEFT JOIN users u ON t.user_id=u.id ORDER BY t.id DESC LIMIT 200').fetchall()
    conn.close()
    return render_template('admin.html', users=users, transactions=txs)

def is_fraud_bla(user, amount, location):
    # Simple Behavior & Location Analysis (BLA)
    # If amount <= limit -> allowed
    limit = user['transaction_limit']
    if amount <= limit:
        return False, 'amount_within_limit'
    # If location differs from last known location -> suspicious
    last_loc = user['last_location'] or ''
    if last_loc and location and location.strip().lower() != last_loc.strip().lower():
        return True, 'location_mismatch'
    # If amount is far above average -> suspicious
    avg = user['avg_amount'] or 0
    tx_count = user['tx_count'] or 0
    if tx_count>0 and avg>0 and amount > avg * 3:
        return True, 'amount_far_above_avg'
    # Velocity check: too many transactions recently
    conn = get_db_conn()
    recent = conn.execute('SELECT COUNT(*) as c FROM transactions WHERE user_id=? AND timestamp>?',
                          (user['id'], (datetime.utcnow() - timedelta(hours=1)).isoformat())).fetchone()
    conn.close()
    if recent and recent['c'] >= 5:
        return True, 'high_velocity'
    # default deny for higher than limit
    return False, 'needs_manual_check'

@app.route('/process_transaction', methods=['POST'])
@login_required
def process_transaction():
    user = current_user()
    amount = float(request.form['amount'])
    location = request.form.get('location','')
    method = request.form.get('method','bla')
    conn = get_db_conn()

    if method == 'bla':
        fraud, reason = is_fraud_bla(user, amount, location)
        status = 'denied' if fraud else 'approved'
        conn.execute('INSERT INTO transactions (user_id,amount,location,timestamp,status,reason) VALUES (?,?,?,?,?,?)',
                 (user['id'], amount, location, datetime.utcnow().isoformat(), status, reason))
        # update user stats on approval
        if not fraud:
            # update avg and last_location
            new_count = (user['tx_count'] or 0) + 1
            new_avg = ((user['avg_amount'] or 0) * (user['tx_count'] or 0) + amount) / new_count
            conn.execute('UPDATE users SET avg_amount=?, tx_count=?, last_location=? WHERE id=?',
                         (new_avg, new_count, location or user['last_location'], user['id']))
        conn.commit()
        conn.close()
        return render_template('transaction_result.html', fraud=fraud, reason=reason, method='BLA')

    # OTP flow
    if method == 'otp':
        code = '{:06d}'.format(random.randint(0,999999))
        expires = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        conn.execute('INSERT INTO otps (user_id,code,expires_at) VALUES (?,?,?)', (user['id'], code, expires))
        conn.commit()
        conn.close()
        print(f'[DEMO] OTP for user {user["username"]}: {code}')
        # store pending transaction in session for demo
        session['pending_tx'] = {'amount': amount, 'location': location}
        return redirect(url_for('verify_otp'))

    conn.close()
    flash('Unknown method', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/verify_otp', methods=['GET','POST'])
@login_required
def verify_otp():
    user = current_user()
    if request.method == 'POST':
        code = request.form['code']
        conn = get_db_conn()
        row = conn.execute('SELECT * FROM otps WHERE user_id=? AND code=? ORDER BY id DESC LIMIT 1', (user['id'], code)).fetchone()
        if row:
            if datetime.fromisoformat(row['expires_at']) < datetime.utcnow():
                flash('OTP expired', 'danger')
                conn.close()
                return redirect(url_for('dashboard'))
            # approve transaction
            pending = session.pop('pending_tx', None)
            if not pending:
                flash('No pending transaction', 'danger')
                conn.close()
                return redirect(url_for('dashboard'))
            conn.execute('INSERT INTO transactions (user_id,amount,location,timestamp,status,reason) VALUES (?,?,?,?,?,?)',
                         (user['id'], pending['amount'], pending['location'], datetime.utcnow().isoformat(), 'approved','otp_verified'))
            # update user stats
            new_count = (user['tx_count'] or 0) + 1
            new_avg = ((user['avg_amount'] or 0) * (user['tx_count'] or 0) + pending['amount']) / new_count
            conn.execute('UPDATE users SET avg_amount=?, tx_count=?, last_location=? WHERE id=?',
                         (new_avg, new_count, pending['location'] or user['last_location'], user['id']))
            conn.commit()
            conn.close()
            flash('Transaction approved via OTP', 'success')
            return redirect(url_for('dashboard'))
        conn.close()
        flash('Invalid OTP', 'danger')
    return render_template('otp.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
