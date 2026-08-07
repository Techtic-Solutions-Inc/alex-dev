"""Integration tests for user signup and email confirmation."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.models.user import User

VALID_SIGNUP_PAYLOAD = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "password": "SecurePassword123!",
    "terms_accepted": True,
}


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_success(mock_send_email, client: TestClient) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/auth/confirm-email?token=test"
    )
    response = client.post("/api/auth/signup", json=VALID_SIGNUP_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"]
    data = body["data"]
    assert data["email"] == "john.doe@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["name"] == "John Doe"
    assert data["id"]
    assert data["title"] == "Account created"
    assert data["description"]
    assert data["redirect"] == "/sign-in"
    assert "password" not in data
    mock_send_email.assert_called_once()


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_alias_path(mock_send_email, client: TestClient) -> None:
    """Frontend ticket path POST /api/signup must behave like /api/auth/signup."""
    mock_send_email.return_value = (
        "http://localhost:8000/api/auth/confirm-email?token=alias"
    )
    payload = {
        **VALID_SIGNUP_PAYLOAD,
        "email": "alias.user@example.com",
    }
    response = client.post("/api/signup", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "alias.user@example.com"
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
    assert body["message"] == "First name is required."
    assert body["error"]["code"] == "MISSING_FIRST_NAME"
    assert body["error"]["details"]["field"] == "first_name"


def test_signup_empty_first_name(client: TestClient) -> None:
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "   ",
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
    assert body["error"]["details"]["field"] == "email"


def test_signup_weak_password(client: TestClient) -> None:
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "weak.pass@example.com",
            "password": "weak",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "WEAK_PASSWORD"
    assert body["error"]["details"]["field"] == "password"


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_duplicate_email(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/auth/confirm-email?token=dup"
    )
    email = "duplicate.signup@example.com"
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "email": email,
        "password": "SecurePassword123!",
        "terms_accepted": True,
    }

    first = client.post("/api/auth/signup", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/signup", json=payload)
    assert second.status_code == 409
    body = second.json()
    assert body["success"] is False
    assert body["message"] == "An account with this email address already exists."
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"
    assert body["error"]["details"]["field"] == "email"

    user = db_session.query(User).filter(User.email == email).first()
    if user is not None:
        db_session.delete(user)
        db_session.commit()


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
    assert body["message"] == (
        "You must accept the Terms of Use and Privacy Policy."
    )
    assert body["error"]["code"] == "TERMS_NOT_ACCEPTED"
    assert body["error"]["details"]["field"] == "terms_accepted"


def test_signup_terms_missing(client: TestClient) -> None:
    response = client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "terms.missing@example.com",
            "password": "SecurePassword123!",
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "TERMS_NOT_ACCEPTED"


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_persists_user(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/auth/confirm-email?token=test"
    )
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
    assert user.last_name == "User"
    assert user.is_email_verified is False
    assert user.email_verification_token is not None

    db_session.delete(user)
    db_session.commit()
