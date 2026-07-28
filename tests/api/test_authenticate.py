
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_successfully_logs_in_with_valid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_user_receives_error_for_invalid_login_attempts(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_user_redirected_to_dashboard_on_successful_login(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == 200
    assert response.json()["redirect_url"] == "/dashboard"


@pytest.mark.asyncio
async def test_email_password_sign_in(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_credential_validation(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_error_handling_for_incorrect_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_redirect_to_dashboard(client: AsyncClient):
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == 200
    assert response.json()["redirect_url"] == "/dashboard"


@pytest.mark.asyncio
async def test_missing_token(client: AsyncClient):
    response = await client.get("/api/v1/protected-resource")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
