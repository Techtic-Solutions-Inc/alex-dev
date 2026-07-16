import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_reset_password_happy_path(async_client: AsyncClient, valid_reset_token):
    response = await async_client.post('/reset-password', json={
        'token': valid_reset_token,
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    })
    assert response.status_code == 200
    assert response.json()['message'] == 'Your password has been reset successfully! You can now log in.'

@pytest.mark.asyncio
async def test_reset_password_edge_case_empty_password(async_client: AsyncClient, valid_reset_token):
    response = await async_client.post('/reset-password', json={
        'token': valid_reset_token,
        'new_password': '',
        'confirm_password': ''
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_reset_password_edge_case_max_length_password(async_client: AsyncClient, valid_reset_token):
    long_password = 'P' * 256
    response = await async_client.post('/reset-password', json={
        'token': valid_reset_token,
        'new_password': long_password,
        'confirm_password': long_password
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_reset_password_error_case_mismatched_passwords(async_client: AsyncClient, valid_reset_token):
    response = await async_client.post('/reset-password', json={
        'token': valid_reset_token,
        'new_password': 'Password123!',
        'confirm_password': 'Password1234!'
    })
    assert response.status_code == 400
    assert response.json()['detail'] == 'Passwords do not match'

@pytest.mark.asyncio
async def test_reset_password_auth_missing_token(async_client: AsyncClient):
    response = await async_client.post('/reset-password', json={
        'new_password': 'Password123!',
        'confirm_password': 'Password123!'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'