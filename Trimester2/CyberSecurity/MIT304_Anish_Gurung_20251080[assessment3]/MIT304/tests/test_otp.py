from app import app, db, User, OTPRecord, OTPEngine


def setup_user(username='test_otp', email='test_otp@example.com'):
    with app.app_context():
        u = User.query.filter_by(username=username).first()
        if u:
            OTPRecord.query.filter_by(user_id=u.id).delete()
            db.session.delete(u)
            db.session.commit()
        u = User(username=username, email=email, home_city='Sydney', home_country='Australia')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        return u.id


def teardown_user(user_id):
    with app.app_context():
        OTPRecord.query.filter_by(user_id=user_id).delete()
        u = User.query.get(user_id)
        if u:
            db.session.delete(u)
        db.session.commit()


def test_generate_and_verify_otp():
    user_id = setup_user('test_otp_2', 'test_otp2@example.com')
    try:
        with app.app_context():
            u = User.query.get(user_id)
            # create a dummy transaction id (None is allowed for OTP generation here)
            otp = OTPEngine.generate(u.id, None)
            assert otp is not None
            code = otp.otp_code
            assert OTPEngine.verify(u.id, code) is True
            # second verify should fail
            assert OTPEngine.verify(u.id, code) is False
    finally:
        teardown_user(user_id)
