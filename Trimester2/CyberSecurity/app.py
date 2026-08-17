import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["DATABASE"] = os.path.join(os.path.dirname(__file__), "security_app.db")


def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            owner TEXT NOT NULL,
            value REAL NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            asset_id INTEGER NOT NULL,
            threat TEXT NOT NULL,
            vulnerability TEXT NOT NULL,
            impact REAL NOT NULL,
            strategy TEXT NOT NULL,
            risk_score REAL NOT NULL,
            ale REAL NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


def current_timestamp():
    return datetime.now(timezone.utc).isoformat()


def get_controls():
    return [
        {
            "name": "MFA",
            "description": "Require a second authentication factor for privileged logins.",
        },
        {
            "name": "Login restrictions",
            "description": "Block repeated invalid attempts and enforce strong passwords.",
        },
        {
            "name": "Geo-blocking",
            "description": "Restrict access from high-risk locations and unusual IP ranges.",
        },
        {
            "name": "Activity monitoring",
            "description": "Monitor unusual access patterns and flag suspicious events.",
        },
    ]


def calculate_risk_score(threat, vulnerability, impact):
    threat_map = {
        "credential": 3,
        "malware": 4,
        "ransom": 5,
        "phishing": 3,
        "insider": 4,
        "default": 2,
    }
    vulnerability_map = {
        "weak": 3,
        "misconfigured": 4,
        "unpatched": 5,
        "exposed": 4,
        "default": 2,
    }

    threat_text = threat.lower()
    vulnerability_text = vulnerability.lower()

    threat_score = next((score for keyword, score in threat_map.items() if keyword in threat_text), threat_map["default"])
    vulnerability_score = next((score for keyword, score in vulnerability_map.items() if keyword in vulnerability_text), vulnerability_map["default"])
    return round(threat_score * vulnerability_score * impact, 2)


def is_suspicious_activity(threat, vulnerability):
    combined = f"{threat} {vulnerability}".lower()
    suspicious_terms = ["credential", "malware", "ransom", "brute", "suspicious", "unusual", "attack"]
    return any(term in combined for term in suspicious_terms)


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html", controls=get_controls())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or len(password) < 8:
            flash("Username required and password must be at least 8 characters.")
            return redirect(url_for("index"))

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), current_timestamp()),
            )
            conn.commit()
            user_row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            session["user_id"] = user_row[0]
            session["username"] = username
            session["failed_attempts"] = 0
            flash("Welcome! Your account has been created.")
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("That username already exists.")
            return redirect(url_for("index"))
        finally:
            conn.close()

    return render_template("index.html", controls=get_controls())


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        failed_attempts = session.get("failed_attempts", 0)

        if failed_attempts >= 3:
            flash("Suspicious activity detected. Access temporarily blocked.")
            return redirect(url_for("index"))

        conn = get_db()
        user = conn.execute("SELECT id, username, password FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["failed_attempts"] = 0
            flash("Login successful.")
            return redirect(url_for("dashboard"))

        session["failed_attempts"] = failed_attempts + 1
        flash("Invalid credentials. Repeated failures may trigger a temporary block.")

    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("index"))

    conn = get_db()
    assets = conn.execute("SELECT * FROM assets WHERE user_id = ? ORDER BY id DESC", (session["user_id"],)).fetchall()
    risks = conn.execute("SELECT * FROM risks WHERE user_id = ? ORDER BY id DESC", (session["user_id"],)).fetchall()
    total_value = sum(asset["value"] for asset in assets)
    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        assets=assets,
        risks=risks,
        controls=get_controls(),
        total_value=round(total_value, 2),
    )


@app.route("/assets", methods=["POST"])
def assets():
    if "user_id" not in session:
        return redirect(url_for("index"))

    name = request.form.get("name", "").strip()
    if not name:
        flash("Asset name is required.")
        return redirect(url_for("dashboard"))

    conn = get_db()
    conn.execute(
        "INSERT INTO assets (user_id, name, asset_type, owner, value, description, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            session["user_id"],
            name,
            request.form.get("asset_type", "Unknown"),
            request.form.get("owner", "Unknown"),
            float(request.form.get("value", 0)),
            request.form.get("description", ""),
            current_timestamp(),
        ),
    )
    conn.commit()
    conn.close()
    flash("Asset added successfully.")
    return redirect(url_for("dashboard"))


@app.route("/risks", methods=["POST"])
def risks():
    if "user_id" not in session:
        return redirect(url_for("index"))

    asset_id = int(request.form.get("asset_id", 0))
    threat = request.form.get("threat", "")
    vulnerability = request.form.get("vulnerability", "")
    impact = float(request.form.get("impact", 0))
    strategy = request.form.get("strategy", "mitigate")

    if is_suspicious_activity(threat, vulnerability):
        flash("Suspicious activity detected and blocked for review.")
        return redirect(url_for("dashboard"))

    risk_score = calculate_risk_score(threat, vulnerability, impact)
    ale = round(impact * 10000, 2)

    conn = get_db()
    conn.execute(
        "INSERT INTO risks (user_id, asset_id, threat, vulnerability, impact, strategy, risk_score, ale, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (session["user_id"], asset_id, threat, vulnerability, impact, strategy, risk_score, ale, current_timestamp()),
    )
    conn.commit()
    conn.close()
    flash("Risk recorded successfully.")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)
