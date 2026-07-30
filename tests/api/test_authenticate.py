

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient, mock_auth0_service):
    mock_auth0_service.authenticate_user.return_value = {
        "access_token": "mock_access_token",
        "id_token": "mock_id_token",
        "expires_in": 3600
    }
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client: AsyncClient, mock_auth0_service):
    mock_auth0_service.authenticate_user.side_effect = Exception("Invalid credentials")
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_user_login_empty_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "", "password": "TestUser123!"}
    )
    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_user_login_empty_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": ""}
    )
    assert response.status_code == 422
    assert "password" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_user_login_missing_token(client: AsyncClient):
    response = await client.get("/api/v1/user/dashboard")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
