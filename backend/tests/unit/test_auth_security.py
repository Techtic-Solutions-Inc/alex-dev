"""Unit coverage for authentication primitives and request validation."""

import pytest
from pydantic import ValidationError

from app.core.security import create_token, decode_token, hash_password, verify_password
from app.schemas.auth import SignupRequest


def test_password_hash_round_trip() -> None:
    """Passwords are salted and can be verified without plaintext persistence."""
    password_hash = hash_password("S3cure!Pass")

    assert password_hash != "S3cure!Pass"
    assert verify_password("S3cure!Pass", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_access_token_round_trip() -> None:
    """Signed access tokens have the expected type and subject."""
    token, _ = create_token("user-123", "access", 300)

    assert decode_token(token, "access")["sub"] == "user-123"


def test_signup_requires_strong_password_and_terms() -> None:
    """The signup DTO rejects invalid frontend form payloads."""
    with pytest.raises(ValidationError):
        SignupRequest(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            password="weakpass",
            terms_accepted=False,
        )
