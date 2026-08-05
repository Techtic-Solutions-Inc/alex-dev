from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from utils.password import verify_password
from utils.token import generate_confirmation_token

STRONG_PASSWORD = "StrongPass1!"


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, db_session: AsyncSession) -> None:
    with patch("api.services.registration_service.send_confirmation_email_async", new_callable=AsyncMock) as mock_send_email:
        response = await client.post(
            "/auth/register",
            json={"email": "newuser@example.com", "password": STRONG_PASSWORD},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "Registration successful" in data["message"]

    result = await db_session.execute(
        select(User).where(User.email == "newuser@example.com")
    )
    user = result.scalar_one()
    assert verify_password(STRONG_PASSWORD, user.hashed_password)
    assert user.is_confirmed is False

    mock_send_email.assert_called_once()
    assert mock_send_email.call_args.args[0] == "newuser@example.com"
    assert mock_send_email.call_args.args[1]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "duplicate@example.com", "password": STRONG_PASSWORD}

    with patch("api.services.registration_service.send_confirmation_email_async", new_callable=AsyncMock):
        first_response = await client.post("/auth/register", json=payload)
        second_response = await client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email already registered."


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"email": "weakpass@example.com", "password": "weak"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password_missing_uppercase(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"email": "weakpass2@example.com", "password": "weakpass1!"},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Password must contain" in detail
    assert "uppercase" in detail


@pytest.mark.asyncio
async def test_register_weak_password_missing_digit(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"email": "weakpass3@example.com", "password": "WeakPass!"},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Password must contain" in detail
    assert "digit" in detail


@pytest.mark.asyncio
async def test_register_weak_password_missing_special(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"email": "weakpass4@example.com", "password": "WeakPass1"},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Password must contain" in detail
    assert "special" in detail


@pytest.mark.asyncio
async def test_register_sends_confirmation_email(client: AsyncClient) -> None:
    with patch("api.services.registration_service.send_confirmation_email_async", new_callable=AsyncMock) as mock_send_email:
        response = await client.post(
            "/auth/register",
            json={"email": "emailtest@example.com", "password": STRONG_PASSWORD},
        )

    assert response.status_code == 201
    mock_send_email.assert_called_once()
    call_args = mock_send_email.call_args.args
    assert call_args[0] == "emailtest@example.com"
    assert len(call_args[1]) > 0


@pytest.mark.asyncio
async def test_register_email_case_insensitive(client: AsyncClient) -> None:
    payload_upper = {"email": "CaseTest@Example.com", "password": STRONG_PASSWORD}
    payload_lower = {"email": "casetest@example.com", "password": STRONG_PASSWORD}

    with patch("api.services.registration_service.send_confirmation_email_async", new_callable=AsyncMock):
        first_response = await client.post("/auth/register", json=payload_upper)
        second_response = await client.post("/auth/register", json=payload_lower)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_register_invalid_email_format(client: AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": STRONG_PASSWORD},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_confirm_email_success(client: AsyncClient, db_session: AsyncSession) -> None:
    with patch("api.services.registration_service.send_confirmation_email_async", new_callable=AsyncMock):
        await client.post(
            "/auth/register",
            json={"email": "confirm@example.com", "password": STRONG_PASSWORD},
        )

    token = generate_confirmation_token("confirm@example.com")
    response = await client.post("/auth/confirm", json={"token": token})

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "confirm@example.com"
    assert "confirmed successfully" in data["message"]

    result = await db_session.execute(
        select(User).where(User.email == "confirm@example.com")
    )
    user = result.scalar_one()
    assert user.is_confirmed is True


@pytest.mark.asyncio
async def test_confirm_email_invalid_token(client: AsyncClient) -> None:
    response = await client.post("/auth/confirm", json={"token": "invalid-token"})

    assert response.status_code == 400
    assert "Invalid confirmation token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_confirm_email_already_confirmed(client: AsyncClient) -> None:
    with patch("api.services.registration_service.send_confirmation_email_async", new_callable=AsyncMock):
        await client.post(
            "/auth/register",
            json={"email": "alreadyconfirmed@example.com", "password": STRONG_PASSWORD},
        )

    token = generate_confirmation_token("alreadyconfirmed@example.com")

    first_response = await client.post("/auth/confirm", json={"token": token})
    assert first_response.status_code == 200

    second_response = await client.post("/auth/confirm", json={"token": token})
    assert second_response.status_code == 200
    assert "already confirmed" in second_response.json()["message"]
