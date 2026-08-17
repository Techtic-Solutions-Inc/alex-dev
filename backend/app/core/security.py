"""Password hashing and JWT creation/verification primitives."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings

_PASSWORD_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    """Return a salted PBKDF2-SHA256 password hash."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _PASSWORD_ITERATIONS
    )
    return f"pbkdf2_sha256${_PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Compare a plaintext password with a stored hash in constant time."""
    try:
        scheme, iterations, salt_hex, digest_hex = stored_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (TypeError, ValueError):
        return False


def create_token(subject: str, token_type: str, expires_in: int) -> tuple[str, datetime]:
    """Create a signed JWT with issuer, audience, type, and unique ID."""
    expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
    payload = {
        "sub": subject,
        "type": token_type,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": datetime.now(UTC),
        "exp": expires_at,
        "jti": str(uuid4()),
    }
    return (
        jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM),
        expires_at,
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    """Verify a JWT and ensure it is being used in the intended flow."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
    except JWTError as exc:
        raise ValueError("Invalid or expired token.") from exc
    if payload.get("type") != expected_type or not payload.get("sub") or not payload.get("jti"):
        raise ValueError("Invalid token type.")
    return payload
