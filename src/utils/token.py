from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from config.settings import JWT_ALGORITHM, JWT_EXPIRY, JWT_SECRET


def _require_secret() -> str:
    if not JWT_SECRET:
        raise ValueError("JWT_SECRET or JWT_SECRET_KEY environment variable is not set")
    return JWT_SECRET


def generate_token(data: dict[str, Any], expires_in_seconds: int | None = None) -> str:
    """Generate a JWT token with the given payload data."""
    secret = _require_secret()
    expiry_seconds = expires_in_seconds if expires_in_seconds is not None else JWT_EXPIRY
    payload = {
        **data,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=expiry_seconds),
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token. Raises jwt.PyJWTError on failure."""
    secret = _require_secret()
    return jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])


def generate_confirmation_token(email: str) -> str:
    """Generate a short-lived token for email confirmation (24h expiry)."""
    return generate_token(
        {"sub": email, "type": "email_confirmation"},
        expires_in_seconds=86400,
    )


def decode_confirmation_token(token: str) -> str:
    """Decode a confirmation token and return the email. Raises ValueError on invalid token."""
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise ValueError("Confirmation token has expired.")
    except jwt.PyJWTError:
        raise ValueError("Invalid confirmation token.")

    if payload.get("type") != "email_confirmation":
        raise ValueError("Invalid confirmation token.")

    email = payload.get("sub")
    if not email:
        raise ValueError("Invalid confirmation token.")

    return email


def generate_session_token(user_id: int, email: str) -> str:
    """Generate a session token for authenticated users."""
    return generate_token(
        {"sub": str(user_id), "email": email, "type": "session"},
    )
