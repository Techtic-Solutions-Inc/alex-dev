"""Integration tests for the login endpoint."""

from fastapi.testclient import TestClient

from src.api.models.user import User
from src.config.settings import get_settings


def test_login_success(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "testuser@example.com"
    assert body["data"]["access_token"]
    assert body["data"]["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPassword123!"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_email_format_validation(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "invalid-email", "password": "TestUser123!"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_login_password_length(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "short"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_login_remember_me(client: TestClient, test_user: User) -> None:
    settings = get_settings()
    response = client.post(
        "/api/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "TestUser123!",
            "remember_me": True,
        },
    )
    assert response.status_code == 200
    assert (
        response.json()["data"]["expires_in"]
        == settings.effective_remember_me_jwt_expiry
    )
