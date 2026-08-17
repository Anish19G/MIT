
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random, string, math, os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fraud_detection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
db = SQLAlchemy(app)


@app.context_processor
def inject_current_year():
    return {'current_year': datetime.utcnow().year}


# ══════════════════════════════════════════════════════════════
# MODELS
# ══════════════════════════════════════════════════════════════

class User(db.Model):
    __tablename__ = 'users'
    id                = db.Column(db.Integer, primary_key=True)
    username          = db.Column(db.String(80), unique=True, nullable=False)
    email             = db.Column(db.String(120), unique=True, nullable=False)
    password_hash     = db.Column(db.String(256), nullable=False)
    transaction_limit = db.Column(db.Float, default=1000.0)
    home_city         = db.Column(db.String(100), default='Sydney')
    home_country      = db.Column(db.String(100), default='Australia')
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    transactions      = db.relationship('Transaction', backref='user', lazy=True)
    otp_records       = db.relationship('OTPRecord', backref='user', lazy=True)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount           = db.Column(db.Float, nullable=False)
    merchant         = db.Column(db.String(200), nullable=False)
    location_city    = db.Column(db.String(100), nullable=False)
    location_country = db.Column(db.String(100), nullable=False)
    ip_address       = db.Column(db.String(50))
    status           = db.Column(db.String(20), default='pending')
    fraud_method     = db.Column(db.String(20))
    bla_score        = db.Column(db.Float)
    is_flagged       = db.Column(db.Boolean, default=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)


class OTPRecord(db.Model):
    __tablename__ = 'otp_records'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'))
    otp_code       = db.Column(db.String(6), nullable=False)
    expires_at     = db.Column(db.DateTime, nullable=False)
    is_used        = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at


# ══════════════════════════════════════════════════════════════
# BLA ENGINE
# ══════════════════════════════════════════════════════════════

class BLAEngine:
    FRAUD_THRESHOLD = 0.60

    CITY_COORDS = {
        'sydney':(-33.87,151.21),'melbourne':(-37.81,144.96),'brisbane':(-27.47,153.03),
        'perth':(-31.95,115.86),'adelaide':(-34.93,138.60),'canberra':(-35.28,149.13),
        'auckland':(-36.85,174.76),'london':(51.51,-0.13),'new york':(40.71,-74.01),
        'los angeles':(34.05,-118.24),'tokyo':(35.69,139.69),'beijing':(39.91,116.39),
        'paris':(48.85,2.35),'dubai':(25.20,55.27),'singapore':(1.35,103.82),
        'mumbai':(19.08,72.88),'toronto':(43.65,-79.38),'chicago':(41.88,-87.63),
        'lagos':(6.52,3.38),'moscow':(55.75,37.62),
    }

    @classmethod
    def haversine(cls, c1, c2):
        if not c1 or not c2:
            return 999
        lat1,lon1 = math.radians(c1[0]),math.radians(c1[1])
        lat2,lon2 = math.radians(c2[0]),math.radians(c2[1])
        a = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
        return 6371 * 2 * math.asin(math.sqrt(a))

    @classmethod
    def amount_score(cls, amount, limit):
        if amount <= limit * 0.5:   return 0.0
        elif amount <= limit:        return 0.2
        elif amount <= limit * 1.5: return 0.5
        elif amount <= limit * 2.0: return 0.7
        else:                        return 0.95

    @classmethod
    def location_score(cls, home_city, tx_city, home_country, tx_country):
        if home_country.lower() != tx_country.lower():
            return 0.85
        dist = cls.haversine(
            cls.CITY_COORDS.get(home_city.lower()),
            cls.CITY_COORDS.get(tx_city.lower())
        )
        if dist < 100:   return 0.0
        elif dist < 500:  return 0.25
        elif dist < 1500: return 0.55
        else:             return 0.80

    @classmethod
    def velocity_score(cls, user_id, window_minutes=60):
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        recent = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= cutoff
        ).count()
        if recent == 0:   return 0.0
        elif recent <= 2:  return 0.1
        elif recent <= 5:  return 0.45
        else:              return 0.80

    @classmethod
    def time_score(cls):
        h = datetime.utcnow().hour
        if 0 <= h < 5:          return 0.60
        elif h < 7 or h >= 22:  return 0.25
        else:                    return 0.0

    @classmethod
    def analyse(cls, user, amount, tx_city, tx_country):
        sa = cls.amount_score(amount, user.transaction_limit)
        sl = cls.location_score(user.home_city, tx_city, user.home_country, tx_country)
        sv = cls.velocity_score(user.id)
        st = cls.time_score()
        composite = sa*0.35 + sl*0.30 + sv*0.20 + st*0.15
        return {
            'composite_score': round(composite, 4),
            'is_fraudulent':   composite >= cls.FRAUD_THRESHOLD,
            'factors': {
                'amount_score':   round(sa,4),
                'location_score': round(sl,4),
                'velocity_score': round(sv,4),
                'time_score':     round(st,4),
            },
            'threshold': cls.FRAUD_THRESHOLD,
        }


# ══════════════════════════════════════════════════════════════
# OTP ENGINE
# ══════════════════════════════════════════════════════════════

class OTPEngine:
    @staticmethod
    def generate(user_id, transaction_id):
        OTPRecord.query.filter_by(user_id=user_id, is_used=False).update({'is_used': True})
        db.session.commit()
        code = ''.join(random.choices(string.digits, k=6))
        otp = OTPRecord(
            user_id=user_id, transaction_id=transaction_id,
            otp_code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=5)
        )
        db.session.add(otp)
        db.session.commit()
        return otp

    @staticmethod
    def verify(user_id, code):
        otp = OTPRecord.query.filter_by(
            user_id=user_id, otp_code=code, is_used=False
        ).order_by(OTPRecord.created_at.desc()).first()
        if otp and otp.is_valid():
            otp.is_used = True
            db.session.commit()
            return True
        return False


# ══════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        city     = request.form.get('home_city','Sydney').strip()
        country  = request.form.get('home_country','Australia').strip()
        limit    = float(request.form.get('transaction_limit', 1000))

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        u = User(username=username, email=email, home_city=city,
                 home_country=country, transaction_limit=limit)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash('Account created. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.permanent = True
            session['user_id']  = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    txs  = Transaction.query.filter_by(user_id=user.id)\
               .order_by(Transaction.created_at.desc()).limit(10).all()
    denied   = Transaction.query.filter_by(user_id=user.id, status='denied').count()
    approved = Transaction.query.filter_by(user_id=user.id, status='approved').count()
    return render_template('dashboard.html', user=user, transactions=txs,
                           total_denied=denied, total_approved=approved)


@app.route('/transaction', methods=['GET','POST'])
def transaction():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if request.method == 'POST':
        amount     = float(request.form.get('amount', 0))
        merchant   = request.form.get('merchant','').strip()
        tx_city    = request.form.get('location_city','').strip()
        tx_country = request.form.get('location_country','').strip()
        method     = request.form.get('detection_method','BLA')

        if amount <= 0:
            flash('Enter a valid amount.', 'danger')
            return render_template('transaction.html', user=user)

        tx = Transaction(user_id=user.id, amount=amount, merchant=merchant,
                         location_city=tx_city, location_country=tx_country,
                         ip_address=request.remote_addr, fraud_method=method)
        db.session.add(tx)
        db.session.flush()

        if method == 'BLA':
            result = BLAEngine.analyse(user, amount, tx_city, tx_country)
            tx.bla_score  = result['composite_score']
            tx.is_flagged = result['is_fraudulent']
            tx.status     = 'denied' if result['is_fraudulent'] else 'approved'
            db.session.commit()
            return render_template('result.html', user=user, tx=tx, result=result,
                                   method='BLA', approved=not result['is_fraudulent'])
        else:
            tx.status = 'pending_otp'
            db.session.commit()
            otp = OTPEngine.generate(user.id, tx.id)
            session['pending_tx_id'] = tx.id
            return render_template('otp_verify.html', user=user, tx=tx,
                                   otp_code=otp.otp_code,
                                   expires_at=otp.expires_at.strftime('%H:%M:%S'))
    return render_template('transaction.html', user=user)


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user     = db.session.get(User, session['user_id'])
    tx_id    = session.get('pending_tx_id')
    tx       = db.session.get(Transaction, tx_id) if tx_id else None
    otp_code = request.form.get('otp_code','').strip()
    if not tx:
        flash('No pending transaction.', 'danger')
        return redirect(url_for('dashboard'))
    if OTPEngine.verify(user.id, otp_code):
        tx.status = 'approved'
        db.session.commit()
        session.pop('pending_tx_id', None)
        return render_template('result.html', user=user, tx=tx,
                               result=None, method='OTP', approved=True)
    else:
        tx.status = 'denied'
        db.session.commit()
        session.pop('pending_tx_id', None)
        return render_template('result.html', user=user, tx=tx,
                               result=None, method='OTP', approved=False)


@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    txs  = Transaction.query.filter_by(user_id=user.id)\
               .order_by(Transaction.created_at.desc()).all()
    return render_template('history.html', user=user, transactions=txs)


@app.route('/api/bla_score', methods=['POST'])
def api_bla_score():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = db.session.get(User, session['user_id'])
    data = request.get_json()
    try:
        result = BLAEngine.analyse(user, float(data.get('amount',0)),
                                   data.get('city',''), data.get('country',''))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='demo').first():
            demo = User(username='demo', email='demo@example.com',
                        home_city='Sydney', home_country='Australia',
                        transaction_limit=1000.0)
            demo.set_password('demo123')
            db.session.add(demo)
            db.session.commit()
            print("Demo user: username=demo  password=demo123")
    app.run(debug=True, port=5000)
