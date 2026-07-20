
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
def setup_user(db_session):
    # Setup code to create a user in the test database
    user = User(email="existing@example.com", password="hashedpassword")
    db_session.add(user)
    db_session.commit()
    return user


def test_register_success(client):
    response = client.post("/api/v1/auth/register", json={"email": "newuser@example.com", "password": "strongpassword"})
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["email"] == "newuser@example.com"


def test_register_duplicate_email(client, setup_user):
    response = client.post("/api/v1/auth/register", json={"email": "existing@example.com", "password": "strongpassword"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_register_invalid_email(client):
    response = client.post("/api/v1/auth/register", json={"email": "invalid-email", "password": "strongpassword"})
    assert response.status_code == 422


def test_register_empty_email(client):
    response = client.post("/api/v1/auth/register", json={"email": "", "password": "strongpassword"})
    assert response.status_code == 422


def test_register_empty_password(client):
    response = client.post("/api/v1/auth/register", json={"email": "newuser@example.com", "password": ""})
    assert response.status_code == 422


def test_register_missing_token(client):
    # Assuming the endpoint requires a token for registration
    response = client.post("/api/v1/auth/register", json={"email": "newuser@example.com", "password": "strongpassword"})
    assert response.status_code == 401
