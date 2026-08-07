"""Integration tests for user signup and email confirmation."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.models.user import User


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_success(mock_send_email, client: TestClient) -> None:
    mock_send_email.return_value = "http://localhost:8000/api/auth/confirm-email?token=test"
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "john.doe@example.com"
    assert body["data"]["first_name"] == "John"
    assert body["data"]["last_name"] == "Doe"
    assert body["data"]["name"] == "John Doe"
    mock_send_email.assert_called_once()


def test_signup_missing_first_name(client: TestClient) -> None:
    response = client.post(
        "/api/auth/signup",
        json={
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "MISSING_FIRST_NAME"
    assert body["error"]["details"]["field"] == "first_name"


def test_signup_invalid_email_format(client: TestClient) -> None:
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Invalid email format."
    assert body["error"]["code"] == "INVALID_EMAIL"


@patch("src.api.routes.signup.create_user_with_confirmation")
def test_signup_duplicate_email(mock_create_user, client: TestClient) -> None:
    from src.exceptions import ConflictError

    mock_create_user.side_effect = ConflictError(
        message="An account with this email address already exists.",
        code="EMAIL_ALREADY_EXISTS",
        details={"field": "email"},
    )
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "duplicate@example.com",
            "password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_signup_terms_not_accepted(client: TestClient) -> None:
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePassword123!",
            "terms_accepted": False,
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "TERMS_NOT_ACCEPTED"
    assert body["error"]["details"]["field"] == "terms_accepted"


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_persists_user(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = "http://localhost:8000/api/auth/confirm-email?token=test"
    email = "persisted.user@example.com"
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "Persisted",
            "last_name": "User",
            "email": email,
            "password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 201

    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.first_name == "Persisted"
    assert user.is_email_verified is False

    db_session.delete(user)
    db_session.commit()
