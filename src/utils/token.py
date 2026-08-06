"""JWT access token utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from src.config.settings import get_settings
from src.exceptions import UnauthorizedError


def generate_access_token(
    data: dict[str, Any],
    *,
    expires_in_seconds: int | None = None,
) -> str:
    """Create a signed JWT access token."""
    settings = get_settings()
    to_encode = data.copy()
    lifetime = (
        expires_in_seconds
        if expires_in_seconds is not None
        else settings.effective_jwt_expiry
    )
    expire = datetime.now(timezone.utc) + timedelta(seconds=lifetime)
    to_encode.update({"exp": expire, "sub": data.get("id")})
    return jwt.encode(
        to_encode,
        settings.effective_jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.effective_jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise UnauthorizedError(message="Invalid or expired token.") from exc
