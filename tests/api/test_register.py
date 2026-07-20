import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post('/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'StrongPassword123!'
    })
    assert response.status_code == 201
    assert response.json()['email'] == 'newuser@example.com'

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user):
    response = await client.post('/auth/register', json={
        'email': 'user@example.com',
        'password': 'AnotherPassword123!'
    })
    assert response.status_code == 409
    assert response.json()['detail'] == 'Email already in use. Please use a different email address.'

@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    response = await client.post('/auth/register', json={
        'email': 'invalid-email',
        'password': 'StrongPassword123!'
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    response = await client.post('/auth/register', json={
        'email': 'anothernewuser@example.com',
        'password': '123'
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    response = await client.post('/auth/register', json={})
    assert response.status_code == 422
