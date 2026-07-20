from datetime import datetime, timedelta, timezone

from src.models.user import User
from src.services.auth_service import hash_password

VALID_TOKEN = "valid-reset-token-xyz789"


def _create_user_with_reset_token(db_session, *, token: str, expires_at: datetime) -> User:
    user = User(
        email="user@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token=token,
        password_reset_token_expires_at=expires_at,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_reset_password_success(client, db_session):
    _create_user_with_reset_token(
        db_session,
        token=VALID_TOKEN,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    redirect_response = client.get(
        f"/reset-password?token={VALID_TOKEN}",
        follow_redirects=False,
    )
    assert redirect_response.status_code == 302
    assert VALID_TOKEN in redirect_response.headers["location"]

    response = client.post(
        "/reset-password",
        json={
            "token": VALID_TOKEN,
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
    )
    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Your password has been reset successfully! You can now log in."
    )

    db_session.expire_all()
    user = db_session.query(User).filter(User.email == "user@example.com").one()
    assert user.password_reset_token is None
    assert user.password_reset_token_expires_at is None


def test_reset_password_invalid_link(client):
    response = client.post(
        "/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired password reset token."


def test_reset_password_mismatched_passwords(client, db_session):
    _create_user_with_reset_token(
        db_session,
        token=VALID_TOKEN,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )

    response = client.post(
        "/reset-password",
        json={
            "token": VALID_TOKEN,
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match."
