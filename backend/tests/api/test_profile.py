# Test cases for profile API

import os
import pytest

# Use environment variables or a secure vault to manage secrets
SECRET_KEY = os.getenv('SECRET_KEY')
API_KEY = os.getenv('API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')

@pytest.fixture
def client():
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_get_profile(client):
    response = client.get("/api/profile")
    assert response.status_code == 200
    assert "profile" in response.json()


def test_update_profile(client):
    response = client.put(
        "/api/profile",
        json={"name": "New Name", "email": "newemail@example.com"},
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_profile(client):
    response = client.delete("/api/profile", headers={"Authorization": f"Bearer {API_KEY}"})
    assert response.status_code == 204
