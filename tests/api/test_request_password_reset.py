import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_request_password_reset_happy_path(async_client: AsyncClient, existing_user_email):
    response = await async_client.post('/email/reset', json={'email': existing_user_email})
    assert response.status_code == 200
    assert 'reset link sent' in response.json()['message']

@pytest.mark.asyncio
async def test_request_password_reset_edge_case_empty_email(async_client: AsyncClient):
    response = await async_client.post('/email/reset', json={'email': ''})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_request_password_reset_edge_case_invalid_email(async_client: AsyncClient):
    response = await async_client.post('/email/reset', json={'email': 'invalid-email'})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_request_password_reset_error_case_nonexistent_email(async_client: AsyncClient):
    response = await async_client.post('/email/reset', json={'email': 'nonexistent@test.com'})
    assert response.status_code == 200
    assert 'reset link sent' in response.json()['message']

@pytest.mark.asyncio
async def test_request_password_reset_auth_missing_token(async_client: AsyncClient):
    response = await async_client.post('/email/reset', json={'email': 'user@test.com'})
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'