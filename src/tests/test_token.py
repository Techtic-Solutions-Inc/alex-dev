from unittest.mock import patch

import jwt
import pytest

from config.settings import JWT_ALGORITHM, JWT_SECRET
from utils.token import (
    decode_confirmation_token,
    decode_token,
    generate_confirmation_token,
    generate_session_token,
    generate_token,
)


class TestGenerateToken:
    def test_returns_decodable_jwt(self) -> None:
        token = generate_token({"sub": "test"})
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == "test"
        assert "exp" in payload

    def test_custom_expiry(self) -> None:
        token = generate_token({"sub": "test"}, expires_in_seconds=60)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == "test"

    def test_raises_without_secret(self) -> None:
        with patch("utils.token.JWT_SECRET", None):
            with pytest.raises(ValueError, match="JWT_SECRET"):
                generate_token({"sub": "test"})


class TestDecodeToken:
    def test_decodes_valid_token(self) -> None:
        token = generate_token({"sub": "hello", "role": "admin"})
        payload = decode_token(token)
        assert payload["sub"] == "hello"
        assert payload["role"] == "admin"

    def test_raises_on_expired_token(self) -> None:
        token = generate_token({"sub": "x"}, expires_in_seconds=-1)
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token)

    def test_raises_on_invalid_token(self) -> None:
        with pytest.raises(jwt.PyJWTError):
            decode_token("not.a.valid.token")


class TestConfirmationToken:
    def test_roundtrip(self) -> None:
        token = generate_confirmation_token("user@example.com")
        email = decode_confirmation_token(token)
        assert email == "user@example.com"

    def test_has_email_confirmation_type(self) -> None:
        token = generate_confirmation_token("user@example.com")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["type"] == "email_confirmation"
        assert payload["sub"] == "user@example.com"

    def test_expired_token_raises_valueerror(self) -> None:
        token = generate_token(
            {"sub": "x@y.com", "type": "email_confirmation"},
            expires_in_seconds=-1,
        )
        with pytest.raises(ValueError, match="expired"):
            decode_confirmation_token(token)

    def test_wrong_type_raises_valueerror(self) -> None:
        token = generate_token({"sub": "x@y.com", "type": "session"})
        with pytest.raises(ValueError, match="Invalid"):
            decode_confirmation_token(token)

    def test_missing_sub_raises_valueerror(self) -> None:
        token = generate_token({"type": "email_confirmation"})
        with pytest.raises(ValueError, match="Invalid"):
            decode_confirmation_token(token)


class TestSessionToken:
    def test_contains_user_info(self) -> None:
        token = generate_session_token(42, "admin@example.com")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == "42"
        assert payload["email"] == "admin@example.com"
        assert payload["type"] == "session"
