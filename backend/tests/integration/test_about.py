import pytest
from httpx import AsyncClient

from app.main import app

@pytest.mark.asyncio
async def test_get_about_happy_path(async_client: AsyncClient):
    response = await async_client.get("/api/about")
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'team_members' in data['data']
    assert 'marketing_content' in data['data']

@pytest.mark.asyncio
async def test_get_about_missing_terms(async_client: AsyncClient):
    response = await async_client.post("/api/about/contact", json={"phone": "+1-555-0100"})
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert data['message'] == "Validation error"

@pytest.mark.asyncio
async def test_get_about_invalid_phone(async_client: AsyncClient):
    response = await async_client.post("/api/about/contact", json={"phone": "invalid", "terms_accepted": True})
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert data['message'] == "Validation error"
