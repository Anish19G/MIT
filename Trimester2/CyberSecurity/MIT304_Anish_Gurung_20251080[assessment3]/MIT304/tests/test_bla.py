from app import app, db, User, Transaction, BLAEngine
from datetime import datetime, timedelta


def setup_user(username='test_bla', email='test_bla@example.com'):
    with app.app_context():
        u = User.query.filter_by(username=username).first()
        if u:
            # cleanup previous user's transactions
            Transaction.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
            db.session.commit()
        u = User(username=username, email=email, home_city='Sydney', home_country='Australia', transaction_limit=100.0)
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        return u.id


def teardown_user(user_id):
    with app.app_context():
        Transaction.query.filter_by(user_id=user_id).delete()
        u = User.query.get(user_id)
        if u:
            db.session.delete(u)
        db.session.commit()


def test_amount_score_thresholds():
    assert BLAEngine.amount_score(10, 100) == 0.0
    assert BLAEngine.amount_score(60, 100) == 0.2
    assert BLAEngine.amount_score(120, 100) == 0.5
    assert BLAEngine.amount_score(180, 100) == 0.7
    assert BLAEngine.amount_score(250, 100) == 0.95


def test_analyse_flagging_behavior():
    user_id = setup_user('test_bla_2', 'test_bla2@example.com')
    try:
        with app.app_context():
            u = User.query.get(user_id)
            # small tx should not be flagged
            r1 = BLAEngine.analyse(u, 10, 'Sydney', 'Australia')
            assert r1['is_fraudulent'] is False
            # very large foreign tx should be flagged
            r2 = BLAEngine.analyse(u, 5000, 'London', 'United Kingdom')
            assert r2['is_fraudulent'] is True
    finally:
        teardown_user(user_id)


def test_velocity_score_changes():
    user_id = setup_user('test_bla_3', 'test_bla3@example.com')
    try:
        with app.app_context():
            # ensure no recent tx
            Transaction.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            v0 = BLAEngine.velocity_score(user_id, window_minutes=60)
            assert v0 == 0.0
            # create 3 recent transactions
            now = datetime.utcnow()
            for i in range(3):
                tx = Transaction(user_id=user_id, amount=5+i, merchant=f'M{i}', location_city='Sydney', location_country='Australia', created_at=now - timedelta(minutes=10*i))
                db.session.add(tx)
            db.session.commit()
            v1 = BLAEngine.velocity_score(user_id, window_minutes=60)
            assert v1 > 0.0
    finally:
        teardown_user(user_id)
