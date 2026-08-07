import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    response = await async_client.post('/api/auth/login', json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()['success'] is True

@pytest.mark.asyncio
async def test_login_empty_fields(async_client: AsyncClient):
    response = await async_client.post('/api/auth/login', json={})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_incorrect_password(async_client: AsyncClient):
    response = await async_client.post('/api/auth/login', json={"email": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_without_token(async_client: AsyncClient):
    response = await async_client.get('/api/auth/session')
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_auth0_integration(async_client: AsyncClient):
    # Mock Auth0 response and test integration
    pass