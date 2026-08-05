from unittest.mock import AsyncMock, patch

import jwt
import pytest
from httpx import AsyncClient

from config.settings import JWT_ALGORITHM, JWT_SECRET

STRONG_PASSWORD = "StrongPass1!"


async def _register_user(client: AsyncClient, email: str, password: str = STRONG_PASSWORD) -> None:
    with patch("api.services.registration_service.send_confirmation_email_async", new_callable=AsyncMock):
        response = await client.post(
            "/auth/register",
            json={"email": email, "password": password},
        )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await _register_user(client, "loginuser@example.com")

    response = await client.post(
        "/auth/login",
        json={"email": "loginuser@example.com", "password": STRONG_PASSWORD},
    )

    assert response.status_code == 200
    data = response.json()
    assert "session_token" in data
    assert isinstance(data["session_token"], str)
    assert data["session_token"]

    payload = jwt.decode(
        data["session_token"],
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
    )
    assert payload["email"] == "loginuser@example.com"
    assert payload["type"] == "session"
    assert payload["sub"]


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient) -> None:
    await _register_user(client, "wrongpass@example.com")

    response = await client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "WrongPass1!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": STRONG_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": STRONG_PASSWORD},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_password(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": ""},
    )

    assert response.status_code == 422
