import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    response = await client.post('/auth/login', json={
        'email': 'user@test.com',
        'password': 'TestUser123!'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post('/auth/login', json={
        'email': 'user@test.com',
        'password': 'WrongPassword'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'

@pytest.mark.asyncio
async def test_login_missing_email(client: AsyncClient):
    response = await client.post('/auth/login', json={
        'password': 'TestUser123!'
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_missing_password(client: AsyncClient):
    response = await client.post('/auth/login', json={
        'email': 'user@test.com'
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient):
    response = await client.post('/auth/login', json={
        'email': 'inactive@test.com',
        'password': 'TestUser123!'
    })
    assert response.status_code == 403
    assert response.json()['detail'] == 'User account is inactive'
