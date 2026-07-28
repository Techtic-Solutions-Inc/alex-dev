
import pytest


@pytest.mark.asyncio
async def test_user_login_success(client, mocker):
    mocker.patch('src.services.auth_service.verify_password', return_value=True)
    response = await client.post('/api/v1/user/authenticate', json={
        'email': 'user@test.com',
        'password': 'TestUser123!'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()


@pytest.mark.asyncio
async def test_user_login_invalid_credentials(client, mocker):
    mocker.patch('src.services.auth_service.verify_password', return_value=False)
    response = await client.post('/api/v1/user/authenticate', json={
        'email': 'user@test.com',
        'password': 'WrongPassword'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'


@pytest.mark.asyncio
async def test_user_login_empty_email(client):
    response = await client.post('/api/v1/user/authenticate', json={
        'email': '',
        'password': 'TestUser123!'
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_login_empty_password(client):
    response = await client.post('/api/v1/user/authenticate', json={
        'email': 'user@test.com',
        'password': ''
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_login_missing_token(client):
    response = await client.get('/api/v1/user/dashboard')
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'
