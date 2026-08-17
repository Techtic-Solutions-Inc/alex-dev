"""JWT creation and validation helpers."""

from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt

from app.core.config import get_settings

TokenKind = Literal["access", "refresh"]


class InvalidTokenError(ValueError):
    """Raised when a token is malformed, expired, or used for the wrong purpose."""


def create_token(subject: str, token_type: TokenKind, expires_in: int) -> str:
    """Create a signed token for the given subject and explicit token purpose."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    """Create a short-lived access token."""
    return create_token(subject, "access", get_settings().jwt_expiry)


def create_refresh_token(subject: str) -> str:
    """Create a refresh token that can only be used at the refresh endpoint."""
    return create_token(subject, "refresh", get_settings().jwt_refresh_expiry)


def decode_token(token: str, expected_type: TokenKind) -> dict[str, Any]:
    """Validate a token's signature, expiry, subject, and intended purpose."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError("The supplied token is invalid or expired.") from exc

    if payload.get("type") != expected_type or not isinstance(payload.get("sub"), str):
        raise InvalidTokenError("The supplied token is invalid or expired.")
    return payload
