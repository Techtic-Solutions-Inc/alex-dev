

import pytest
from httpx import AsyncClient

from src.api.services.auth0_service import Auth0AuthenticationService


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, mocker):
    mock_auth0 = mocker.patch.object(Auth0AuthenticationService, 'authenticate', return_value={
        'sub': 'auth0|123456',
        'email': 'user@example.com'
    })
    response = await client.post('/api/auth/login', json={
        'email': 'user@example.com',
        'password': 'securePassword123'
    })
    assert response.status_code == 201
    assert 'access_token' in response.json()['data']
    mock_auth0.assert_called_once()

@pytest.mark.asyncio
async def test_login_empty_fields(client: AsyncClient):
    response = await client.post('/api/auth/login', json={
        'email': '',
        'password': ''
    })
    assert response.status_code == 400
    assert response.json()['message'] == 'Email is required.'

@pytest.mark.asyncio
async def test_login_incorrect_password(client: AsyncClient, mocker):
    mock_auth0 = mocker.patch.object(Auth0AuthenticationService, 'authenticate', side_effect=UnauthorizedError)
    response = await client.post('/api/auth/login', json={
        'email': 'user@example.com',
        'password': 'wrongPassword'
    })
    assert response.status_code == 409
    assert response.json()['message'] == 'Incorrect password.'
    mock_auth0.assert_called_once()

@pytest.mark.asyncio
async def test_access_protected_route_without_token(client: AsyncClient):
    response = await client.get('/api/auth/session')
    assert response.status_code == 403
    assert response.json()['message'] == 'Forbidden.'
