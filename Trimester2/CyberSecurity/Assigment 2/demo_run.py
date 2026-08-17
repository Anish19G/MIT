import requests
import sqlite3
import time

base = 'http://127.0.0.1:5000'
s = requests.Session()

def register_and_login():
    print('Registering demo_user...')
    s.post(base + '/register', data={'username':'demo_user','password':'password123','limit':'100','location':'CityA'})
    time.sleep(0.2)
    print('Logging in...')
    s.post(base + '/login', data={'username':'demo_user','password':'password123'})
    time.sleep(0.2)

def send_bla(amount, location):
    print(f'POST BLA transaction amount={amount} location={location}')
    r = s.post(base + '/process_transaction', data={'amount':amount, 'location':location, 'method':'bla'})
    print('--- Response snippet ---')
    print(r.text[:400])
    print('------------------------')

def send_otp_flow(amount, location):
    print(f'POST OTP transaction amount={amount} location={location}')
    r = s.post(base + '/process_transaction', data={'amount':amount, 'location':location, 'method':'otp'}, allow_redirects=True)
    time.sleep(0.2)
    # read OTP from DB
    conn = sqlite3.connect('app.db')
    row = conn.execute('SELECT code, expires_at FROM otps WHERE id=(SELECT MAX(id) FROM otps)').fetchone()
    conn.close()
    if row:
        code = row[0]
        print('Found OTP in DB:', code)
        rv = s.post(base + '/verify_otp', data={'code':code})
        print('Verify response snippet:')
        print(rv.text[:400])
    else:
        print('No OTP found in DB')

if __name__ == '__main__':
    register_and_login()
    # Approved: within limit
    send_bla(50, 'CityA')
    time.sleep(0.3)
    # Denied: above limit and different location -> BLA flags location_mismatch
    send_bla(500, 'CityB')
    time.sleep(0.3)
    # OTP flow: request OTP then verify using DB value
    send_otp_flow(300, 'CityA')
