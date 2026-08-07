import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(async_client: AsyncClient):
    response = await async_client.post('/api/auth/signup', json={"email": "newuser@example.com", "password": "password123", "first_name": "John", "last_name": "Doe", "terms_accepted": True})
    assert response.status_code == 201
    assert response.json()['success'] is True

@pytest.mark.asyncio
async def test_signup_missing_first_name(async_client: AsyncClient):
    response = await async_client.post('/api/auth/signup', json={"email": "newuser@example.com", "password": "password123", "terms_accepted": True})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_signup_invalid_email(async_client: AsyncClient):
    response = await async_client.post('/api/auth/signup', json={"email": "invalidemail", "password": "password123", "first_name": "John", "last_name": "Doe", "terms_accepted": True})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_signup_duplicate_email(async_client: AsyncClient):
    response = await async_client.post('/api/auth/signup', json={"email": "existinguser@example.com", "password": "password123", "first_name": "John", "last_name": "Doe", "terms_accepted": True})
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_signup_terms_not_accepted(async_client: AsyncClient):
    response = await async_client.post('/api/auth/signup', json={"email": "newuser@example.com", "password": "password123", "first_name": "John", "last_name": "Doe", "terms_accepted": False})
    assert response.status_code == 422