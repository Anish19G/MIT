# Final Report — Fraud Detection Web App (BLA vs OTP)

## 1. Introduction

This project implements a web application to detect and block fraudulent transactions using Behavior and Location Analysis (BLA) and an alternative One-Time Password (OTP) flow. The system supports user registration, secure login, transaction requests, fraud detection, and administrator oversight.

## 2. System Design

- Backend: Flask + SQLite (simple, portable)
- Authentication: password hashing using Werkzeug, session-based auth with 30-minute timeout
- Fraud detection: BLA heuristics with reasons logged per transaction, and OTP fallback.

## 3. BLA Heuristics

Implemented heuristics:
- Transaction limit check: transactions below user limit are allowed.
- Location mismatch: transaction from a different city than the user's last known location is suspicious.
- Amount vs historical average: transactions > 3x user average are suspicious.
- Velocity: >=5 transactions within 1 hour flagged as high velocity.

Each flagged transaction stores a `reason` to help analysts.

## 4. OTP Flow

OTP codes are generated server-side (6-digit) and expire after 5 minutes. For the demo, OTPs are printed to console and stored in the `otps` table; in production use an SMS/email gateway.

## 5. Admin Interface

Accessible to the `admin` user. Shows users and recent transactions with reasons and statuses for auditing.

## 6. Evaluation and Demo Results

Run the included `demo_run.py` after starting the server to reproduce the demo:
- A small transaction within limit is approved by BLA.
- A high-value transaction from a different location is flagged and denied by BLA.
- An OTP flow can approve otherwise suspicious transactions.

Example metrics from a demo run (single-user):
- BLA true positive: detected location mismatch on a high transaction.
- OTP success: validated and approved.

## 7. Comparison: BLA vs OTP

- BLA: Low user friction (transparent), real-time automatic blocking, but can produce false positives when users legitimately travel or have atypical behaviour. Requires accurate location and behavioral history.
- OTP: High assurance (possession factor), reduces false positives by verifying user control, but adds friction and requires a reliable delivery channel.

Recommendation: Use BLA for low-risk transactions and challenge with OTP for high-risk or uncertain transactions.

## 8. How to Run

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. To run tests:

```bash
venv\Scripts\pytest -q
```

## 9. Next Improvements

- Integrate real geo-IP lookup for location analysis.
- Use background job queue for OTP delivery.
- Add rate-limiting and CAPTCHA to reduce automated abuse.
- Persist logs to a more scalable DB and add visual analytics.

## 10. Files of Interest

- `app.py` — main application and BLA logic
- `templates/` — UI templates
- `demo_run.py` — reproduces demo scenarios
- `final_report.md` — this report
