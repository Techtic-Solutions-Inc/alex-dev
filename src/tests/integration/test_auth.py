"""Integration tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.config.settings import get_settings
from src.utils.password import hash_password


def test_login_success(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Signed in successfully."
    data = body["data"]
    assert data["email"] == "testuser@example.com"
    assert data["id"] == str(test_user.id)
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0
    assert isinstance(data["expires_in"], int)
    assert data["title"] == "Welcome back"
    assert data["message"] == "You have signed in successfully."
    assert data["description"] == (
        "Everything you need to create standout real estate content."
    )
    assert data["link"] == "/dashboard"
    assert data["redirect"] == "/dashboard"


def test_login_remember_me_extends_session(
    client: TestClient,
    test_user: User,
) -> None:
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
    body = response.json()
    assert body["data"]["expires_in"] == settings.effective_remember_me_jwt_expiry
    assert body["data"]["expires_in"] > settings.effective_jwt_expiry


def test_login_without_remember_me_uses_default_expiry(
    client: TestClient,
    test_user: User,
) -> None:
    settings = get_settings()
    response = client.post(
        "/api/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "TestUser123!",
            "remember_me": False,
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["expires_in"] == settings.effective_jwt_expiry


def test_login_invalid_password(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Invalid email or password."
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_user(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "SomePassword1!"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_validation_missing_fields(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation Error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["detail"] == "Validation Error"
    assert isinstance(body["errors"], list)
    assert len(body["errors"]) >= 2


def test_login_validation_empty_strings(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "", "password": ""},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_login_validation_invalid_email_format(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "not-an-email", "password": "ValidPass1!"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert any(error["field"] == "email" for error in body["errors"])


def test_login_validation_password_too_short(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": "short"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert any(error["field"] == "password" for error in body["errors"])


def test_validate_session_requires_auth(client: TestClient) -> None:
    response = client.get("/api/auth/validate")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_validate_session_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/auth/validate",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_validate_session_accepts_valid_token(
    client: TestClient,
    test_user: User,
) -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get(
        "/api/auth/validate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Session is valid."
    data = body["data"]
    assert data["id"] == str(test_user.id)
    assert data["email"] == "testuser@example.com"
    assert data["title"] == "Session active"
    assert data["message"] == "Your session is active."
    assert data["description"] == "You are signed in to Agentwise."
    assert data["link"] == "/dashboard"
    assert data["redirect"] == "/dashboard"


def test_get_session_requires_auth(client: TestClient) -> None:
    response = client.get("/api/auth/session")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_get_session_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/auth/session",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_get_session_accepts_valid_token(
    client: TestClient,
    test_user: User,
) -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get(
        "/api/auth/session",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Session is valid."
    data = body["data"]
    assert data["id"] == str(test_user.id)
    assert data["email"] == "testuser@example.com"
    assert data["title"] == "Session active"
    assert data["message"] == "Your session is active."
    assert data["description"] == "You are signed in to Agentwise."
    assert data["link"] == "/dashboard"
    assert data["redirect"] == "/dashboard"


def test_login_with_auth0_enabled(
    client: TestClient,
    test_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When Auth0 is configured, credentials are validated via Auth0 before login."""
    from src.api.services import auth_service

    class FakeAuth0:
        is_enabled = True

        def authenticate(self, email: str, password: str) -> dict:
            assert email == "testuser@example.com"
            assert password == "TestUser123!"
            return {"access_token": "auth0-token"}

    monkeypatch.setattr(
        auth_service,
        "get_auth0_service",
        lambda settings=None: FakeAuth0(),
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["email"] == "testuser@example.com"


def test_auth0_webhook_accepts_valid_request(client: TestClient) -> None:
    response = client.post(
        "/api/auth/auth0/webhook",
        json={"type": "user.created"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["received"] is True


def test_protected_endpoint_requires_auth(client: TestClient) -> None:
    response = client.get("/protected-endpoint")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_protected_endpoint_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/protected-endpoint",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_protected_endpoint_accepts_valid_token(
    client: TestClient,
    test_user: User,
) -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]

    response = client.get(
        "/protected-endpoint",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"user": str(test_user.id)}


def test_duplicate_user_email_conflict(db_session: Session) -> None:
    first = User(
        username="user_one",
        first_name="User",
        last_name="One",
        email="duplicate@example.com",
        password_hash=hash_password("Password123!"),
    )
    duplicate = User(
        username="user_two",
        first_name="User",
        last_name="Two",
        email="duplicate@example.com",
        password_hash=hash_password("Password123!"),
    )
    db_session.add(first)
    db_session.commit()

    db_session.add(duplicate)
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()

    db_session.delete(first)
    db_session.commit()
