# Fraud Detection Web App (BLA + OTP)

This project implements a web application for transaction fraud detection using Behavior & Location Analysis (BLA) and an OTP alternative.

Main features:
- User registration and login (secure password hashing)
- Transaction submission with BLA-based real-time decisioning
- OTP fallback to verify and approve transactions
- Admin dashboard for auditing users and transactions
- Unit tests for BLA logic

Run locally (Windows):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

To run the demo script which automates several scenarios:

```powershell
venv\Scripts\python demo_run.py
```

To run unit tests:

```powershell
venv\Scripts\pytest -q
```

Notes:
- OTPs are printed to the server console and stored in the DB for the demo. Replace with SMS/email in production.
- Create an admin user by registering with username `admin` to view the admin dashboard at `/admin`.
