from src.models.user import User
from src.services.auth_service import verify_password


def _mock_send_confirmation_email(monkeypatch):
    sent_emails: list[dict[str, str]] = []

    def mock_send(to_email: str, confirmation_token: str) -> None:
        sent_emails.append({"to": to_email, "token": confirmation_token})

    monkeypatch.setattr(
        "src.services.registration_service.send_confirmation_email",
        mock_send,
    )
    return sent_emails


def test_register_success(client, db_session, monkeypatch):
    sent_emails = _mock_send_confirmation_email(monkeypatch)

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "StrongPass1"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "newuser@example.com"
    assert "Registration successful" in body["message"]

    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == "newuser@example.com"
    assert sent_emails[0]["token"]

    user = db_session.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.email_confirmed is False
    assert user.email_confirmation_token == sent_emails[0]["token"]
    assert verify_password("StrongPass1", user.hashed_password)


def test_register_duplicate_email(client, sample_user, monkeypatch):
    _mock_send_confirmation_email(monkeypatch)

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "testuser@example.com", "password": "StrongPass1"},
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Email already in use. Please use a different email address."
    )
