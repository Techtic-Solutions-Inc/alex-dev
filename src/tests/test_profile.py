from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from utils.token import generate_session_token

STRONG_PASSWORD = "StrongPass1!"
PROFILE_URL = "/api/profile"


async def _create_user(
    client: AsyncClient,
    email: str = "profile@example.com",
    password: str = STRONG_PASSWORD,
) -> dict:
    """Register a user and return login response data with session_token."""
    with patch(
        "api.services.registration_service.send_confirmation_email_async",
        new_callable=AsyncMock,
    ):
        resp = await client.post(
            "/auth/register",
            json={"email": email, "password": password},
        )
    assert resp.status_code == 201

    resp = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200
    return resp.json()


def _auth_headers(session_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {session_token}"}


# ── GET /api/profile ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_profile_success(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    response = await client.get(PROFILE_URL, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profile@example.com"
    assert "id" in data
    assert "first_name" in data
    assert "last_name" in data
    assert "mobile_number" in data
    assert "bio" in data
    assert "address" in data
    assert "profile_picture" in data


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient) -> None:
    response = await client.get(PROFILE_URL)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_get_profile_invalid_token(client: AsyncClient) -> None:
    headers = _auth_headers("invalid.jwt.token")

    response = await client.get(PROFILE_URL, headers=headers)

    assert response.status_code == 403


# ── PUT /api/profile ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_profile_success(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    update_payload = {
        "first_name": "John",
        "last_name": "Doe",
        "mobile_number": "+1234567890",
        "bio": "Hello world",
        "address": "123 Main St",
        "profile_picture": "https://example.com/photo.jpg",
    }

    response = await client.put(PROFILE_URL, json=update_payload, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "profile@example.com"
    assert data["mobile_number"] == "+1234567890"
    assert data["bio"] == "Hello world"
    assert data["address"] == "123 Main St"
    assert data["profile_picture"] == "https://example.com/photo.jpg"


@pytest.mark.asyncio
async def test_update_profile_returns_updated_details(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    await client.put(
        PROFILE_URL,
        json={"first_name": "Jane"},
        headers=headers,
    )

    response = await client.get(PROFILE_URL, headers=headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"


@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    response = await client.put(
        PROFILE_URL,
        json={"bio": "Updated bio"},
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "Updated bio"
    assert data["email"] == "profile@example.com"


@pytest.mark.asyncio
async def test_update_profile_invalid_email(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    response = await client.put(
        PROFILE_URL,
        json={"email": "not-valid-email"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_profile_invalid_email_format_400(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    response = await client.put(
        PROFILE_URL,
        json={"email": "bad@@email"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_profile_unauthenticated(client: AsyncClient) -> None:
    response = await client.put(
        PROFILE_URL,
        json={"first_name": "Hacker"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_update_profile_invalid_mobile_number(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    response = await client.put(
        PROFILE_URL,
        json={"mobile_number": "abc123"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "mobile number" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_profile_email_change(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    response = await client.put(
        PROFILE_URL,
        json={"email": "newemail@example.com"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"


@pytest.mark.asyncio
async def test_update_profile_duplicate_email(client: AsyncClient) -> None:
    await _create_user(client, email="user1@example.com")
    login_data = await _create_user(client, email="user2@example.com")
    headers = _auth_headers(login_data["session_token"])

    response = await client.put(
        PROFILE_URL,
        json={"email": "user1@example.com"},
        headers=headers,
    )

    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_profile_empty_first_name(client: AsyncClient) -> None:
    login_data = await _create_user(client)
    headers = _auth_headers(login_data["session_token"])

    response = await client.put(
        PROFILE_URL,
        json={"first_name": "   "},
        headers=headers,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_profile_expired_token(client: AsyncClient, db_session: AsyncSession) -> None:
    from datetime import datetime, timedelta, timezone

    import jwt as pyjwt

    from config.settings import JWT_ALGORITHM, JWT_SECRET

    token = pyjwt.encode(
        {
            "sub": "999",
            "email": "expired@example.com",
            "type": "session",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    headers = _auth_headers(token)

    response = await client.get(PROFILE_URL, headers=headers)

    assert response.status_code == 403
    assert "expired" in response.json()["detail"].lower()
