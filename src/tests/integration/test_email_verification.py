"""Integration tests for email verification."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.models.user import User
from src.utils.password import hash_password

VALID_VERIFY_PAYLOAD = {
    "email": "verify.user@example.com",
    "terms_accepted": True,
}


def _create_unverified_user(db_session, email: str = "verify.user@example.com") -> User:
    """Persist an unverified user for verification tests."""
    existing = db_session.query(User).filter(User.email == email).first()
    if existing is not None:
        db_session.delete(existing)
        db_session.commit()

    user = User(
        username="verifyuser",
        first_name="Verify",
        last_name="User",
        email=email,
        password_hash=hash_password("SecurePassword123!"),
        is_email_verified=False,
        email_verification_token="old-token",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@patch("src.api.services.user_service.send_email_verification_email")
def test_email_verification_valid_email(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/auth/confirm-email?token=new-token"
    )
    user = _create_unverified_user(db_session)

    response = client.post("/api/email/verify", json=VALID_VERIFY_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Verification email sent successfully."
    data = body["data"]
    assert data["id"] == str(user.id)
    assert data["email"] == "verify.user@example.com"
    assert data["first_name"] == "Verify"
    assert data["address"] == "verify.user@example.com"
    assert data["title"] == "Verify your email address"
    assert data["description"]
    assert data["link"]
    mock_send_email.assert_called_once()
    sent_token = mock_send_email.call_args.kwargs["verification_token"]

    db_session.refresh(user)
    assert user.email_verification_token == sent_token
    assert user.email_verification_token != "old-token"

    db_session.delete(user)
    db_session.commit()


def test_email_verification_invalid_email_format(client: TestClient) -> None:
    response = client.post(
        "/api/email/verify",
        json={"email": "invalid-email", "terms_accepted": True},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Invalid email format."
    assert body["error"]["code"] == "INVALID_EMAIL"
    assert body["error"]["details"]["field"] == "email"


@patch("src.api.services.user_service.send_email_verification_email")
def test_email_verification_duplicate_email(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    email = "verified.user@example.com"
    existing = db_session.query(User).filter(User.email == email).first()
    if existing is not None:
        db_session.delete(existing)
        db_session.commit()

    user = User(
        username="verifieduser",
        first_name="Verified",
        last_name="User",
        email=email,
        password_hash=hash_password("SecurePassword123!"),
        is_email_verified=True,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/email/verify",
        json={"email": email, "terms_accepted": True},
    )
    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "An account with this email address already exists."
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"
    assert body["error"]["details"]["field"] == "email"
    mock_send_email.assert_not_called()

    db_session.delete(user)
    db_session.commit()


def test_email_verification_terms_not_accepted(client: TestClient) -> None:
    response = client.post(
        "/api/email/verify",
        json={"email": "user@example.com", "terms_accepted": False},
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == (
        "You must accept the Terms of Use and Privacy Policy."
    )
    assert body["error"]["code"] == "TERMS_NOT_ACCEPTED"
    assert body["error"]["details"]["field"] == "terms_accepted"


@patch("src.api.services.user_service.send_email_verification_email")
def test_email_verification_sends_via_sendgrid(
    mock_send_email,
    client: TestClient,
    db_session,
) -> None:
    mock_send_email.return_value = (
        "http://localhost:8000/api/auth/confirm-email?token=sendgrid-token"
    )
    user = _create_unverified_user(db_session, email="sendgrid.user@example.com")

    response = client.post(
        "/api/email/verify",
        json={"email": "sendgrid.user@example.com", "terms_accepted": True},
    )
    assert response.status_code == 201
    mock_send_email.assert_called_once_with(
        recipient_email="sendgrid.user@example.com",
        recipient_first_name="Verify",
        verification_token=mock_send_email.call_args.kwargs["verification_token"],
        settings=mock_send_email.call_args.kwargs["settings"],
    )

    db_session.delete(user)
    db_session.commit()
