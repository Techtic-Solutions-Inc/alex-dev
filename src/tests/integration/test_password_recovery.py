"""Integration tests for password recovery endpoints."""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.models.user import User
from src.utils.password import hash_password, verify_password

VALID_RECOVERY_PAYLOAD = {
    "email": "recovery.user@example.com",
    "terms_accepted": True,
}


def _create_user(db_session, email: str = "recovery.user@example.com") -> User:
    user = User(
        username="recoveryuser",
        first_name="Recovery",
        last_name="User",
        email=email,
        password_hash=hash_password("OldPassword123!"),
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@patch("src.api.services.auth_service.send_password_reset_email")
def test_request_password_reset_valid_email(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/password-recovery/validate/test-token"
    )
    user = _create_user(db_session)

    response = client.post("/api/password-recovery", json=VALID_RECOVERY_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Password reset link sent successfully."
    data = body["data"]
    assert data["id"] == str(user.id)
    assert data["email"] == user.email
    assert data["title"] == "Check your email"
    assert data["description"]
    assert data["link"]
    mock_send_email.assert_called_once()

    db_session.refresh(user)
    assert user.password_reset_token is not None
    assert user.password_reset_token_expires_at is not None

    db_session.delete(user)
    db_session.commit()


def test_request_password_reset_invalid_email_format(client: TestClient) -> None:
    response = client.post(
        "/api/password-recovery",
        json={"email": "invalid-email", "terms_accepted": True},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Invalid email format."
    assert body["error"]["code"] == "INVALID_EMAIL"
    assert body["error"]["details"]["field"] == "email"


def test_request_password_reset_non_existent_email(client: TestClient) -> None:
    response = client.post(
        "/api/password-recovery",
        json={"email": "missing.user@example.com", "terms_accepted": True},
    )
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "No account is registered with this email address."
    assert body["error"]["code"] == "EMAIL_NOT_FOUND"
    assert body["error"]["details"]["field"] == "email"


def test_request_password_reset_empty_email(client: TestClient) -> None:
    response = client.post(
        "/api/password-recovery",
        json={"email": "", "terms_accepted": True},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] in {"EMPTY_EMAIL", "INVALID_EMAIL"}


def test_request_password_reset_terms_not_accepted(client: TestClient) -> None:
    response = client.post(
        "/api/password-recovery",
        json={"email": "recovery.user@example.com", "terms_accepted": False},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == (
        "You must accept the Terms of Use and Privacy Policy."
    )
    assert body["error"]["code"] == "TERMS_NOT_ACCEPTED"
    assert body["error"]["details"]["field"] == "terms_accepted"


@patch("src.api.services.auth_service.send_password_reset_email")
def test_password_reset_link_expiry(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/password-recovery/validate/expired-token"
    )
    user = _create_user(db_session, email="expiry.user@example.com")

    response = client.post(
        "/api/password-recovery",
        json={"email": "expiry.user@example.com", "terms_accepted": True},
    )
    assert response.status_code == 201

    db_session.refresh(user)
    token = user.password_reset_token
    assert token is not None

    user.password_reset_token_expires_at = datetime.now(timezone.utc) - timedelta(
        minutes=1
    )
    db_session.commit()

    validate_response = client.get(f"/api/password-recovery/validate/{token}")
    assert validate_response.status_code == 400
    body = validate_response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "RESET_TOKEN_EXPIRED"

    reset_response = client.post(
        "/api/password-recovery/reset",
        json={
            "token": token,
            "password": "NewPassword123!",
            "terms_accepted": True,
        },
    )
    assert reset_response.status_code == 400
    assert reset_response.json()["error"]["code"] == "RESET_TOKEN_EXPIRED"

    db_session.delete(user)
    db_session.commit()


@patch("src.api.services.auth_service.send_password_reset_email")
def test_validate_reset_token_success(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/password-recovery/validate/valid-token"
    )
    user = _create_user(db_session, email="validate.user@example.com")

    request_response = client.post(
        "/api/password-recovery",
        json={"email": "validate.user@example.com", "terms_accepted": True},
    )
    assert request_response.status_code == 201

    db_session.refresh(user)
    token = user.password_reset_token
    assert token is not None

    validate_response = client.get(f"/api/password-recovery/validate/{token}")
    assert validate_response.status_code == 200
    body = validate_response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(user.id)
    assert body["data"]["email"] == user.email
    assert body["data"]["link"] == "/reset-password"

    db_session.delete(user)
    db_session.commit()


@patch("src.api.services.auth_service.send_password_reset_email")
def test_reset_password_success(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/password-recovery/validate/reset-token"
    )
    user = _create_user(db_session, email="reset.user@example.com")

    request_response = client.post(
        "/api/password-recovery",
        json={"email": "reset.user@example.com", "terms_accepted": True},
    )
    assert request_response.status_code == 201

    db_session.refresh(user)
    token = user.password_reset_token
    assert token is not None

    reset_response = client.post(
        "/api/password-recovery/reset",
        json={
            "token": token,
            "password": "NewPassword123!",
            "terms_accepted": True,
        },
    )
    assert reset_response.status_code == 200
    body = reset_response.json()
    assert body["success"] is True
    assert body["data"]["link"] == "/sign-in"

    db_session.refresh(user)
    assert user.password_reset_token is None
    assert user.password_reset_token_expires_at is None
    assert verify_password("NewPassword123!", user.password_hash)

    db_session.delete(user)
    db_session.commit()


def test_reset_password_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/api/password-recovery/reset",
        json={
            "token": "nonexistent-token",
            "password": "NewPassword123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "INVALID_RESET_TOKEN"
