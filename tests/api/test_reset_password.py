from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

from src.models.user import User
from src.services.auth_service import hash_password
from src.services.password_reset_service import (
    EXPIRED_TOKEN_MESSAGE,
    PASSWORD_RESET_REQUEST_PATH,
)

EXPIRED_TOKEN = "expired-reset-token-abc123"
VALID_TOKEN = "valid-reset-token-xyz789"


def _create_user_with_reset_token(
    db_session,
    *,
    email: str,
    token: str,
    expires_at: datetime,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password("oldpassword"),
        password_reset_token=token,
        password_reset_token_expires_at=expires_at,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_expired_token(client, db_session):
    _create_user_with_reset_token(
        db_session,
        email="expired@example.com",
        token=EXPIRED_TOKEN,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )

    response = client.get(
        f"/api/v1/auth/reset-password?token={EXPIRED_TOKEN}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"].startswith(PASSWORD_RESET_REQUEST_PATH)
    assert EXPIRED_TOKEN_MESSAGE in unquote(response.headers["location"])

    body_text = response.text
    assert EXPIRED_TOKEN not in body_text
    assert "expired@example.com" not in body_text

    post_response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": EXPIRED_TOKEN, "new_password": "newpassword1"},
    )
    assert post_response.status_code == 410
    body = post_response.json()["detail"]
    assert body["message"] == EXPIRED_TOKEN_MESSAGE
    assert body["redirect_url"] == PASSWORD_RESET_REQUEST_PATH
    assert EXPIRED_TOKEN not in str(body)
    assert "expired@example.com" not in str(body)


def test_valid_token(client, db_session):
    _create_user_with_reset_token(
        db_session,
        email="valid@example.com",
        token=VALID_TOKEN,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    response = client.get(f"/api/v1/auth/reset-password?token={VALID_TOKEN}")

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["message"] == "Token is valid."

    reset_response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": VALID_TOKEN, "new_password": "newpassword1"},
    )
    assert reset_response.status_code == 200
    assert reset_response.json()["message"] == "Password has been reset successfully."

    login_response = client.post(
        "/api/v1/login",
        json={"email": "valid@example.com", "password": "newpassword1"},
    )
    assert login_response.status_code == 200
