
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_login_success(client: AsyncClient, admin_user_token: str):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "admin@test.com", "password": "TestAdmin123!"},
        headers={"Authorization": f"Bearer {admin_user_token}"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "admin@test.com", "password": "WrongPassword123!"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_user_login_empty_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "", "password": "TestAdmin123!"}
    )
    assert response.status_code == 422
    assert "email" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_user_login_empty_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "admin@test.com", "password": ""}
    )
    assert response.status_code == 422
    assert "password" in response.json()["detail"][0]["loc"]


@pytest.mark.asyncio
async def test_user_login_missing_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "admin@test.com", "password": "TestAdmin123!"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
