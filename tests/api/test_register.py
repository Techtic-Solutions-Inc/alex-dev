
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_users():
    # Setup test users in the database
    # This should ideally be done using a database fixture
    pass

@pytest.mark.usefixtures("setup_test_users")
def test_register_success():
    response = client.post("/auth/register", json={"email": "newuser@test.com", "password": "NewUser123!"})
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@test.com"

@pytest.mark.usefixtures("setup_test_users")
def test_register_duplicate_email():
    response = client.post("/auth/register", json={"email": "user@test.com", "password": "AnotherPass123!"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already in use. Please use a different email address."}

@pytest.mark.usefixtures("setup_test_users")
def test_register_invalid_email_format():
    response = client.post("/auth/register", json={"email": "invalid-email", "password": "ValidPass123!"})
    assert response.status_code == 422

@pytest.mark.usefixtures("setup_test_users")
def test_register_weak_password():
    response = client.post("/auth/register", json={"email": "unique@test.com", "password": "123"})
    assert response.status_code == 422

@pytest.mark.usefixtures("setup_test_users")
def test_register_missing_token():
    response = client.get("/some_protected_route")
    assert response.status_code == 401
