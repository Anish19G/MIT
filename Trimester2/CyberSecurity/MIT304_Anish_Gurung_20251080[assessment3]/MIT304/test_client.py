from app import app

with app.test_client() as c:
    r = c.get('/')
    print('STATUS', r.status_code)
    print(r.data.decode(errors='ignore')[:1200])
