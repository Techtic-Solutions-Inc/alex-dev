import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):
    response = await client.post('/login', json={
        'email': 'user@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()

@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user):
    response = await client.post('/login', json={
        'email': 'user@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'

@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post('/login', json={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'

@pytest.mark.asyncio
async def test_login_empty_email(client: AsyncClient):
    response = await client.post('/login', json={
        'email': '',
        'password': 'password123'
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_empty_password(client: AsyncClient):
    response = await client.post('/login', json={
        'email': 'user@example.com',
        'password': ''
    })
    assert response.status_code == 422
