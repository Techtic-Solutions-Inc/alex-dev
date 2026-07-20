"""Tests for backend setup: database and JWT authentication."""

from datetime import timedelta

import jwt

from src.config.settings import get_settings
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.utils.password import verify_password


def test_database_connection(db_session) -> None:
    """Database session can persist and retrieve a user record."""
    user = UserService(db_session).create_user("dbtest@example.com", "StrongPass1!")
    assert user.id is not None
    assert user.email == "dbtest@example.com"


def test_jwt_authentication(db_session) -> None:
    """JWT tokens can be created and decoded for authenticated users."""
    settings = get_settings()
    email = "jwttest@example.com"
    password = "StrongPass1!"

    user = UserService(db_session).create_user(email, password)
    auth_service = AuthService(db_session)
    token = auth_service.create_access_token(
        subject=user.email,
        expires_delta=timedelta(minutes=5),
    )

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload["sub"] == email
    assert verify_password(password, user.hashed_password)
