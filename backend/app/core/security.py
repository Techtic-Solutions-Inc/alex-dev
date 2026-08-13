from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"

PASSWORD_RESET_TOKEN_TYPE = "password_reset"


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRY)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_password_reset_token(
    user_id: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT used exclusively for password reset links."""
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRY)
    )
    to_encode: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "type": PASSWORD_RESET_TOKEN_TYPE,
        "exp": expire,
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc


def verify_password_reset_token(token: str) -> dict[str, Any]:
    """Decode and validate a password-reset JWT; reject expired or wrong-type tokens."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired password reset token") from exc

    if payload.get("type") != PASSWORD_RESET_TOKEN_TYPE:
        raise ValueError("Invalid or expired password reset token")

    if not payload.get("sub") or not payload.get("email"):
        raise ValueError("Invalid or expired password reset token")

    return payload


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
