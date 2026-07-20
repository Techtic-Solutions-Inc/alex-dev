import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_login_success():
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post("/auth/login", json={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}

def test_login_logging():
    # Assuming logging is set up to capture login attempts
    pass