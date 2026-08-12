# Test file for sign-in functionality

import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Load environment variables for testing
os.environ['JWT_SECRET'] = 'test_secret_key'
os.environ['DATABASE_URL'] = 'postgresql://test_user:test_password@localhost/test_dbname'


def test_signin_success():
    response = client.post(
        "/api/v1/auth/signin",
        json={"email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["data"]


def test_signin_invalid_credentials():
    response = client.post(
        "/api/v1/auth/signin",
        json={"email": "wrong@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["message"] == "Incorrect email or password"
