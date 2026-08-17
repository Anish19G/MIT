# Fraudulent Transaction Detection (BLA + OTP)

A small Flask app for Behaviour and Location Analysis (BLA) with optional OTP verification.

## Requirements
- Python 3.8+ (project uses a `.venv` in the repo)
- Windows (instructions use PowerShell) or any OS with Python

## Setup (Windows PowerShell)
```powershell
# (optional) create venv if not present
python -m venv .venv
# activate
.\.venv\Scripts\Activate.ps1
# install deps
pip install -r requirements.txt
```

## Run
```powershell
# from project root
.\.venv\Scripts\Activate.ps1
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## Demo account
- username: `demo`
- password: `demo123`

## Notes
- The app creates `fraud_detection.db` (SQLite) in the project dir on first run.
- For OTP mode the generated OTP is shown in the verification page (demo-only).
- I added minimal templates so the UI renders. See the `templates/` directory.


