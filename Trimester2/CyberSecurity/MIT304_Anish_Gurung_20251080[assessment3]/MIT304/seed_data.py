"""Seed script for MIT304 Fraud Detection app
Run with: .\.venv\Scripts\Activate.ps1 ; python seed_data.py
"""
from app import app, db, User, Transaction, OTPRecord, BLAEngine, OTPEngine
from datetime import datetime, timedelta

with app.app_context():
    def get_or_create_user(username, email, city, country, limit, pw):
        u = User.query.filter_by(username=username).first()
        if u:
            print(f"User exists: {u.username} (id={u.id})")
            return u
        u = User(username=username, email=email, home_city=city,
                 home_country=country, transaction_limit=limit)
        u.set_password(pw)
        db.session.add(u)
        db.session.commit()
        print(f"Created user: {u.username} (id={u.id})")
        return u

    # Create sample users
    alice = get_or_create_user('alice','alice@example.com','Sydney','Australia',500.0,'alicepw')
    bob   = get_or_create_user('bob','bob@example.com','London','United Kingdom',2000.0,'bobpw')
    carol = get_or_create_user('carol','carol@example.com','Mumbai','India',1500.0,'carolpw')

    # Helper to create a transaction and apply BLA analysis (simulating route logic)
    def create_tx(user, amount, merchant, city, country, ip='127.0.0.1', method='BLA', created_at=None):
        tx = Transaction(user_id=user.id, amount=amount, merchant=merchant,
                         location_city=city, location_country=country,
                         ip_address=ip, fraud_method=method)
        if created_at:
            tx.created_at = created_at
        db.session.add(tx)
        db.session.flush()
        if method == 'BLA':
            res = BLAEngine.analyse(user, amount, city, country)
            tx.bla_score = res['composite_score']
            tx.is_flagged = res['is_fraudulent']
            tx.status = 'denied' if res['is_fraudulent'] else 'approved'
        else:
            tx.status = 'pending_otp'
            otp = OTPEngine.generate(user.id, tx.id)
            print(f"Generated OTP for tx {tx.id}: {otp.otp_code} (expires {otp.expires_at})")
        db.session.commit()
        print(f"Created tx id={tx.id} user={user.username} amount={tx.amount} status={tx.status} bla={tx.bla_score}")
        return tx

    # Create some transactions
    # Normal small tx for Alice (should be approved)
    create_tx(alice, 30.0, 'Coffee Shop', 'Sydney', 'Australia')

    # Large foreign tx for Alice (likely fraud)
    create_tx(alice, 2000.0, 'Luxury Store', 'London', 'United Kingdom')

    # Bob high-limit user: local expensive purchase (may be ok)
    create_tx(bob, 1200.0, 'Electronics', 'London', 'United Kingdom')

    # Carol: rapid transactions to trigger velocity
    now = datetime.utcnow()
    for i in range(6):
        create_tx(carol, 10.0 + i, f'Snack{i}', 'Mumbai', 'India', created_at=now - timedelta(minutes=5*i))

    # OTP flow example: pending tx for Bob
    create_tx(bob, 5000.0, 'Overseas Purchase', 'New York', 'United States', method='OTP')

    # Summary
    users = User.query.count()
    txs = Transaction.query.count()
    denied = Transaction.query.filter_by(status='denied').count()
    approved = Transaction.query.filter_by(status='approved').count()
    pending = Transaction.query.filter(Transaction.status.like('pending%')).count()
    print('--- Summary ---')
    print(f'Users: {users}')
    print(f'Transactions: {txs} (approved={approved} denied={denied} pending={pending})')
