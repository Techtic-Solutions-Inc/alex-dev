import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_user_registration_success(client: AsyncClient):
    response = await client.post('/api/v1/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'StrongPassword123!',
        'terms_accepted': True
    })
    assert response.status_code == 201
    assert response.json()['email'] == 'john.doe@example.com'

@pytest.mark.asyncio
async def test_user_registration_missing_field(client: AsyncClient):
    response = await client.post('/api/v1/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'StrongPassword123!'
    })
    assert response.status_code == 400
    assert 'terms_accepted' in response.json()['detail']

@pytest.mark.asyncio
async def test_user_registration_duplicate_email(client: AsyncClient, test_db):
    test_db['users'].insert_one({'email': 'john.doe@example.com'})
    response = await client.post('/api/v1/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'StrongPassword123!',
        'terms_accepted': True
    })
    assert response.status_code == 409
    assert 'email' in response.json()['detail']

@pytest.mark.asyncio
async def test_user_registration_weak_password(client: AsyncClient):
    response = await client.post('/api/v1/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'weak',
        'terms_accepted': True
    })
    assert response.status_code == 400
    assert 'password' in response.json()['detail']

@pytest.mark.asyncio
async def test_user_registration_terms_not_accepted(client: AsyncClient):
    response = await client.post('/api/v1/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'StrongPassword123!',
        'terms_accepted': False
    })
    assert response.status_code == 400
    assert 'terms_accepted' in response.json()['detail']