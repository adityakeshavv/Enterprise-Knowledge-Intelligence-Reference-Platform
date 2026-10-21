import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token, decode_access_token

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "manufacturing" in data["available_industries"]

def test_login_success_cxo():
    response = client.post("/api/auth/login", json={
        "username": "cxo_exec",
        "password": "Executive2026!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "CXO"
    assert data["username"] == "cxo_exec"

def test_login_failure_wrong_password():
    response = client.post("/api/auth/login", json={
        "username": "cxo_exec",
        "password": "WrongPassword!"
    })
    assert response.status_code == 401

def test_jwt_encoding_decoding():
    token = create_access_token({"sub": "test_user", "role": "CXO"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test_user"
    assert payload["role"] == "CXO"

def test_get_current_user_profile():
    # Login to obtain token
    login_res = client.post("/api/auth/login", json={
        "username": "cxo_exec",
        "password": "Executive2026!"
    })
    token = login_res.json()["access_token"]
    
    # Request profile
    profile_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    profile = profile_res.json()
    assert profile["username"] == "cxo_exec"
    assert profile["role"] == "CXO"
