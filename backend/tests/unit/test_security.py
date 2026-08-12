from datetime import timedelta

import pytest
from app.core.security import create_access_token, verify_token
from app.exceptions.http_exceptions import UnauthorizedException
from app.middleware.auth import get_current_user


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


@pytest.mark.asyncio
async def test_get_current_user_missing_token_raises_unauthorized() -> None:
    with pytest.raises(UnauthorizedException) as exc_info:
        await get_current_user(token=None)

    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.code == "UNAUTHORIZED"
    assert exc.message == "Authentication required"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_raises_unauthorized() -> None:
    with pytest.raises(UnauthorizedException) as exc_info:
        await get_current_user(token="not-a-valid-jwt")

    exc = exc_info.value
    assert exc.status_code == 401
    assert exc.code == "INVALID_TOKEN"
    assert exc.message == "Invalid or expired token"


@pytest.mark.asyncio
async def test_get_current_user_valid_token_returns_payload() -> None:
    token = create_access_token({"sub": "user@test.com"})
    payload = await get_current_user(token=token)
    assert payload["sub"] == "user@test.com"
