"""Integration tests for user signup and email confirmation endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.models.user import User


@pytest.fixture
def signup_payload() -> dict[str, object]:
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "newuser@example.com",
        "password": "StrongPassword123!",
        "terms_accepted": True,
    }


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_success(
    mock_send_email,
    client: TestClient,
    db_session: Session,
    signup_payload: dict[str, object],
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/auth/confirm-email?token=test-token"
    )

    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 201

    body = response.json()
    assert body["success"] is True
    assert body["message"]
    assert body["data"]["email"] == signup_payload["email"]
    assert body["data"]["first_name"] == signup_payload["first_name"]
    assert body["data"]["last_name"] == signup_payload["last_name"]
    assert body["data"]["name"] == "John Doe"
    assert body["data"]["redirect"] == "/sign-in"
    assert body["data"]["id"]
    assert body["data"]["title"] == "Account created"
    assert body["data"]["message"]
    assert body["data"]["description"]

    user = (
        db_session.query(User)
        .filter(User.email == signup_payload["email"])
        .first()
    )
    assert user is not None
    assert user.first_name == signup_payload["first_name"]
    assert user.last_name == signup_payload["last_name"]
    assert user.is_email_verified is False
    assert user.email_verification_token is not None

    mock_send_email.assert_called_once()
    call_kwargs = mock_send_email.call_args.kwargs
    assert call_kwargs["recipient_email"] == signup_payload["email"]
    assert call_kwargs["recipient_first_name"] == signup_payload["first_name"]
    assert call_kwargs["confirmation_token"] == user.email_verification_token

    db_session.delete(user)
    db_session.commit()


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_missing_first_name(
    mock_send_email,
    client: TestClient,
    signup_payload: dict[str, object],
) -> None:
    payload = {key: value for key, value in signup_payload.items() if key != "first_name"}

    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "MISSING_FIRST_NAME"
    assert body["error"]["details"] == {"field": "first_name"}
    assert body["message"]

    mock_send_email.assert_not_called()


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_invalid_email(
    mock_send_email,
    client: TestClient,
    signup_payload: dict[str, object],
) -> None:
    signup_payload["email"] = "not-an-email"

    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_EMAIL"
    assert body["message"]

    mock_send_email.assert_not_called()


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_duplicate_email(
    mock_send_email,
    client: TestClient,
    test_user: User,
    signup_payload: dict[str, object],
) -> None:
    signup_payload["email"] = test_user.email

    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 409

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"
    assert body["error"]["details"] == {"field": "email"}

    mock_send_email.assert_not_called()


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_terms_not_accepted(
    mock_send_email,
    client: TestClient,
    signup_payload: dict[str, object],
) -> None:
    signup_payload["terms_accepted"] = False

    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "TERMS_NOT_ACCEPTED"
    assert body["error"]["details"] == {"field": "terms_accepted"}
    assert body["message"]

    mock_send_email.assert_not_called()


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_weak_password(
    mock_send_email,
    client: TestClient,
    signup_payload: dict[str, object],
) -> None:
    signup_payload["password"] = "weak"

    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "WEAK_PASSWORD"

    mock_send_email.assert_not_called()


@patch("src.api.services.user_service.send_confirmation_email")
def test_signup_password_missing_special_character(
    mock_send_email,
    client: TestClient,
    signup_payload: dict[str, object],
) -> None:
    signup_payload["password"] = "StrongPassword123"

    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 400
    assert response.json()["success"] is False
    mock_send_email.assert_not_called()


@patch("src.api.services.user_service.send_confirmation_email")
def test_confirm_email_success(
    mock_send_email,
    client: TestClient,
    db_session: Session,
    signup_payload: dict[str, object],
) -> None:
    mock_send_email.return_value = "http://localhost:8000/api/auth/confirm-email?token=x"

    signup_response = client.post("/api/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201

    user = (
        db_session.query(User)
        .filter(User.email == signup_payload["email"])
        .first()
    )
    assert user is not None
    token = user.email_verification_token

    response = client.get("/api/auth/confirm-email", params={"token": token})
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == signup_payload["email"]
    assert body["data"]["id"] == str(user.id)
    assert body["data"]["title"] == "Email confirmed"
    assert body["data"]["link"] == "/sign-in"

    db_session.refresh(user)
    assert user.is_email_verified is True
    assert user.email_verification_token is None

    db_session.delete(user)
    db_session.commit()


def test_confirm_email_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/auth/confirm-email",
        params={"token": "invalid-token-value"},
    )
    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CONFIRMATION_TOKEN"
