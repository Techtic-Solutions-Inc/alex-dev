import pytest
from httpx import AsyncClient
from unittest.mock import patch

from src.api.models.user import User
from src.utils.password import hash_password

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session):
    user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash=hash_password("TestUser123!")
    )
    db_session.add(user)
    db_session.commit()

    response = await client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPassword123!"}
    )
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

@pytest.mark.asyncio
async def test_login_email_format_validation(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "invalid-email", "password": "TestUser123!"}
    )
    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

@pytest.mark.asyncio
async def test_login_password_length(client: AsyncClient):
    response = await client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "short"}
    )
    assert response.status_code == 422
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

@pytest.mark.asyncio
@patch("src.api.services.auth_service.remember_me")
async def test_login_remember_me(mock_remember_me, client: AsyncClient):
    mock_remember_me.return_value = True
    response = await client.post(
        "/api/auth/login",
        json={"email": "testuser@example.com", "password": "TestUser123!", "remember_me": True}
    )
    assert response.status_code == 200
    mock_remember_me.assert_called_once()
