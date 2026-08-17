import os
import tempfile

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test_app.db"
    app_module.app.config.update(TESTING=True, DATABASE=str(db_path))
    app_module.init_db()
    with app_module.app.test_client() as client:
        yield client


def test_register_login_and_dashboard(client):
    response = client.post(
        "/register",
        data={"username": "alice", "password": "SecurePass123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data

    login_response = client.post(
        "/login",
        data={"username": "alice", "password": "SecurePass123!"},
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert b"Dashboard" in login_response.data


def test_add_asset_and_risk(client):
    client.post(
        "/register",
        data={"username": "bob", "password": "SecurePass123!"},
        follow_redirects=True,
    )
    client.post(
        "/login",
        data={"username": "bob", "password": "SecurePass123!"},
        follow_redirects=True,
    )

    asset_response = client.post(
        "/assets",
        data={
            "name": "Payroll Database",
            "asset_type": "Database",
            "owner": "Finance",
            "value": "100000",
            "description": "Stores payroll records",
        },
        follow_redirects=True,
    )
    assert asset_response.status_code == 200
    assert b"Payroll Database" in asset_response.data

    risk_response = client.post(
        "/risks",
        data={
            "asset_id": "1",
            "threat": "Credential stuffing",
            "vulnerability": "Weak password policy",
            "impact": "5",
            "strategy": "mitigate",
        },
        follow_redirects=True,
    )
    assert risk_response.status_code == 200
    assert b"Suspicious activity detected" in risk_response.data


def test_login_block_after_repeated_failures(client):
    client.post(
        "/register",
        data={"username": "charlie", "password": "SecurePass123!"},
        follow_redirects=True,
    )

    for _ in range(4):
        client.post(
            "/login",
            data={"username": "charlie", "password": "wrong-password"},
            follow_redirects=True,
        )

    blocked_response = client.post(
        "/login",
        data={"username": "charlie", "password": "SecurePass123!"},
        follow_redirects=True,
    )
    assert blocked_response.status_code == 200
    assert b"temporarily blocked" in blocked_response.data
