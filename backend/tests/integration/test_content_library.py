import pytest
from httpx import AsyncClient

from app.main import app

@pytest.mark.asyncio
async def test_get_user_details_happy_path(async_client: AsyncClient, user_token_headers):
    response = await async_client.get("/api/content-library/user-details", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'name' in data['data']
    assert 'ai_credit_usage' in data['data']

@pytest.mark.asyncio
async def test_get_user_details_forbidden(async_client: AsyncClient, other_user_token_headers):
    response = await async_client.get("/api/content-library/user-details", headers=other_user_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert data['success'] is False
    assert data['message'] == "You cannot access another user's details"
