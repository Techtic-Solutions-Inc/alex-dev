import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_rate_limiting_happy_path(async_client: AsyncClient):
    # Simulate requests to trigger rate limiting
    for _ in range(5):
        response = await async_client.get('/some-endpoint')
        assert response.status_code == 200

    # This request should be rate limited
    response = await async_client.get('/some-endpoint')
    assert response.status_code == 429
    assert response.json()['detail'] == 'Rate limit exceeded'

@pytest.mark.asyncio
async def test_rate_limiting_edge_case_empty_ip(async_client: AsyncClient):
    response = await async_client.get('/some-endpoint', headers={'X-Forwarded-For': ''})
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_rate_limiting_edge_case_max_requests(async_client: AsyncClient):
    for _ in range(10):
        response = await async_client.get('/some-endpoint')
    assert response.status_code == 429

@pytest.mark.asyncio
async def test_rate_limiting_error_case_invalid_ip(async_client: AsyncClient):
    response = await async_client.get('/some-endpoint', headers={'X-Forwarded-For': 'invalid-ip'})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_rate_limiting_auth_missing_token(async_client: AsyncClient):
    response = await async_client.get('/some-endpoint')
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'