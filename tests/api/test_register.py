from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.user import User
from src.utils.security import verify_password

STRONG_PASSWORD = "Password1!"


@patch("src.api.v1.services.auth_service.send_confirmation_email")
def test_register_success(
    mock_send_email,
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": STRONG_PASSWORD},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["message"] == "User registered successfully"
    assert "id" in data

    user = db_session.query(User).filter(User.email == "newuser@example.com").one()
    assert verify_password(STRONG_PASSWORD, user.hashed_password)
    assert user.is_active is True

    mock_send_email.assert_called_once_with("newuser@example.com")


@patch("src.api.v1.services.auth_service.send_confirmation_email")
def test_register_duplicate_email(
    mock_send_email,
    client: TestClient,
    test_user: User,
) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": STRONG_PASSWORD},
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Email already in use. Please use a different email address."
    )
    mock_send_email.assert_not_called()


def test_register_email_validation(client: TestClient) -> None:
    invalid_email = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": STRONG_PASSWORD},
    )
    assert invalid_email.status_code == 422

    weak_password = client.post(
        "/auth/register",
        json={"email": "valid@example.com", "password": "weak"},
    )
    assert weak_password.status_code == 422
    assert "Password must be at least 8 characters" in str(weak_password.json())
