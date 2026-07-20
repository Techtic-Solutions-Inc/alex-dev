import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
async def setup_user():
    # Setup code to create a user in the test database
    pass


def test_register_success(setup_user):
    response = client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "strongpassword"})
    assert response.status_code == 200
    assert "id" in response.json()


def test_register_duplicate_email(setup_user):
    response = client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "strongpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_invalid_email():
    response = client.post("/api/v1/auth/register", json={"email": "invalid-email", "password": "strongpassword"})
    assert response.status_code == 422