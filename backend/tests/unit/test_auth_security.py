"""Unit tests for password hashing and JWT helpers."""

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import (
    create_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_produces_verifiable_hash() -> None:
    stored = hash_password("StrongPassword123!")

    assert stored.startswith("pbkdf2_sha256$")
    assert verify_password("StrongPassword123!", stored) is True
    assert verify_password("WrongPassword123!", stored) is False


def test_verify_password_rejects_malformed_hash() -> None:
    assert verify_password("StrongPassword123!", "not-a-valid-hash") is False


def test_create_and_decode_access_token() -> None:
    token, expires_at = create_token("user-123", "access", 3600)

    claims = decode_token(token, "access")
    assert claims["sub"] == "user-123"
    assert claims["type"] == "access"
    assert claims["iss"] == settings.JWT_ISSUER
    assert claims["aud"] == settings.JWT_AUDIENCE
    assert expires_at > datetime.now(UTC)


def test_decode_token_rejects_wrong_type() -> None:
    token, _ = create_token("user-123", "refresh", 3600)

    with pytest.raises(ValueError, match="Invalid token type"):
        decode_token(token, "access")


def test_decode_token_rejects_tampered_signature() -> None:
    token, _ = create_token("user-123", "access", 3600)
    tampered = jwt.encode(
        jwt.get_unverified_claims(token) | {"sub": "other-user"},
        "wrong-secret",
        algorithm=settings.JWT_ALGORITHM,
    )

    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token(tampered, "access")


def test_decode_token_rejects_expired_token() -> None:
    expires_at = datetime.now(UTC) - timedelta(seconds=1)
    payload = {
        "sub": "user-123",
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "iat": datetime.now(UTC),
        "exp": expires_at,
        "jti": "expired-token",
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token(token, "access")
