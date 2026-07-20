from datetime import datetime, timedelta, timezone

import pytest

from src.models.user import User
from src.schemas.auth import ResetPasswordRequest
from src.services.auth import hash_password, reset_password, validate_reset_token, verify_password
from tests.conftest import EXPIRED_RESET_TOKEN, VALID_RESET_TOKEN


def test_hash_password():
    hashed = hash_password("SecurePassword123!")
    assert hashed != "SecurePassword123!"
    assert verify_password("SecurePassword123!", hashed)
    assert not verify_password("WrongPassword123!", hashed)


def test_validate_reset_token(db_session):
    user = User(
        email="validate@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token=VALID_RESET_TOKEN,
        password_reset_token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()

    validated_user = validate_reset_token(db_session, VALID_RESET_TOKEN)
    assert validated_user.email == "validate@example.com"


def test_validate_reset_token_invalid(db_session):
    with pytest.raises(ValueError, match="Invalid or expired reset link"):
        validate_reset_token(db_session, "missing-token")


def test_validate_reset_token_expired(db_session):
    user = User(
        email="expired@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token=EXPIRED_RESET_TOKEN,
        password_reset_token_expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()

    with pytest.raises(ValueError, match="Invalid or expired reset link"):
        validate_reset_token(db_session, EXPIRED_RESET_TOKEN)


def test_reset_password_clears_token(db_session):
    user = User(
        email="reset@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token=VALID_RESET_TOKEN,
        password_reset_token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()

    response = reset_password(
        db_session,
        ResetPasswordRequest(
            token=VALID_RESET_TOKEN,
            new_password="NewPassword123!",
            confirm_password="NewPassword123!",
        ),
    )

    assert (
        response.message
        == "Your password has been reset successfully! You can now log in."
    )
    db_session.refresh(user)
    assert user.password_reset_token is None
    assert user.password_reset_token_expires_at is None
    assert verify_password("NewPassword123!", user.hashed_password)
