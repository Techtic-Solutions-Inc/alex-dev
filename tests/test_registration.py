import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, mocker):
    mock_send_email = mocker.patch('utils.email.send_confirmation_email', return_value=None)
    response = await client.post('/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'StrongPassword123!'
    })
    assert response.status_code == 201
    assert response.json()['email'] == 'newuser@example.com'
    mock_send_email.assert_called_once()

@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient):
    response = await client.post('/auth/register', json={
        'email': 'user@test.com',
        'password': 'StrongPassword123!'
    })
    assert response.status_code == 409
    assert response.json()['detail'] == 'Email already registered'

@pytest.mark.asyncio
async def test_register_user_weak_password(client: AsyncClient):
    response = await client.post('/auth/register', json={
        'email': 'uniqueuser@example.com',
        'password': 'weak'
    })
    assert response.status_code == 400
    assert response.json()['detail'] == 'Password does not meet strength requirements'

@pytest.mark.asyncio
async def test_register_user_missing_email(client: AsyncClient):
    response = await client.post('/auth/register', json={
        'password': 'StrongPassword123!'
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_user_missing_password(client: AsyncClient):
    response = await client.post('/auth/register', json={
        'email': 'uniqueuser@example.com'
    })
    assert response.status_code == 422
