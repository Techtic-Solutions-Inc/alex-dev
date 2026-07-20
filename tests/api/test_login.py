
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
def test_login_success():
    response = client.post("/auth/login", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.usefixtures("setup_test_users")
def test_login_invalid_credentials():
    response = client.post("/auth/login", json={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}

@pytest.mark.usefixtures("setup_test_users")
def test_login_empty_username():
    response = client.post("/auth/login", json={"username": "", "password": "testpassword"})
    assert response.status_code == 422

@pytest.mark.usefixtures("setup_test_users")
def test_login_empty_password():
    response = client.post("/auth/login", json={"username": "testuser", "password": ""})
    assert response.status_code == 422

@pytest.mark.usefixtures("setup_test_users")
def test_login_missing_token():
    response = client.get("/some_protected_route")
    assert response.status_code == 401
