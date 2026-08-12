from datetime import timedelta

import pytest

from app.core.security import create_access_token, verify_token


def test_create_access_token() -> None:
    data = {"sub": "user-123"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_token() -> None:
    data = {"sub": "user-123"}
    token = create_access_token(data, expires_delta=timedelta(minutes=5))
    payload = verify_token(token)
    assert payload["sub"] == "user-123"


def test_verify_token_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid or expired token"):
        verify_token("invalid-token")
