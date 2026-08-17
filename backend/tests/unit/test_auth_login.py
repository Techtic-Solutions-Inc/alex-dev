"""Unit coverage for the Sign In request and session behavior."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.core.security import hash_password
from app.exceptions.http_exceptions import APIException
from app.schemas.auth import LoginRequest
from app.services.auth import AuthService


class InMemoryUserRepository:
    """Minimal repository double that records issued refresh sessions."""

    def __init__(self, user: dict[str, object] | None) -> None:
        self._user = user
        self.sessions: list[tuple[str, str, datetime]] = []

    def get_by_email(self, _: str) -> dict[str, object] | None:
        """Return the configured account for a credential lookup."""
        return self._user

    def store_refresh_token(
        self, token_id: str, user_id: str, expires_at: datetime
    ) -> None:
        """Record the refresh session the service creates."""
        self.sessions.append((token_id, user_id, expires_at))


def _user(*, is_active: bool = True) -> dict[str, object]:
    """Build an account compatible with the authentication service."""
    return {
        "id": "7a95c2ce-2d3d-4ff4-8d27-6f40ecae6efa",
        "first_name": "Ada",
        "last_name": "Lovelace",
        "email": "ada@example.com",
        "password_hash": hash_password("Password123"),
        "is_active": is_active,
        "email_verified": True,
    }


def test_login_accepts_valid_credentials_and_returns_token_alias() -> None:
    """A valid active account receives a JWT and frontend-compatible token field."""
    repository = InMemoryUserRepository(_user())

    result = AuthService(repository).login(
        LoginRequest(email="ada@example.com", password="Password123")
    )

    assert result["token"] == result["access_token"]
    assert result["user"]["email"] == "ada@example.com"
    assert len(repository.sessions) == 1


def test_login_rejects_inactive_account() -> None:
    """An otherwise valid inactive account cannot create a session."""
    service = AuthService(InMemoryUserRepository(_user(is_active=False)))

    with pytest.raises(APIException) as error:
        service.login(LoginRequest(email="ada@example.com", password="Password123"))

    assert error.value.status_code == 403
    assert error.value.code == "ACCOUNT_INACTIVE"


def test_login_rejects_incorrect_password() -> None:
    """Incorrect credentials preserve the generic unauthorized error."""
    service = AuthService(InMemoryUserRepository(_user()))

    with pytest.raises(APIException) as error:
        service.login(LoginRequest(email="ada@example.com", password="Wrongpass123"))

    assert error.value.status_code == 401
    assert error.value.code == "INVALID_CREDENTIALS"


@pytest.mark.parametrize(
    "password",
    ["short1A", "lowercase123", "UPPERCASE123", "NoNumbersHere"],
)
def test_login_password_policy(password: str) -> None:
    """The login form requires the documented minimum password strength."""
    with pytest.raises(ValidationError):
        LoginRequest(email="ada@example.com", password=password)


def test_login_rejects_invalid_email() -> None:
    """The typed login body rejects malformed email addresses."""
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="Password123")
