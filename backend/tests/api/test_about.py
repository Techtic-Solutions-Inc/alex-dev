import pytest
from httpx import AsyncClient

from app.main import app

@pytest.mark.asyncio
async def test_get_about_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/about")
        assert response.status_code == 200
        assert "team_members" in response.json()["data"]

@pytest.mark.asyncio
async def test_submit_contact_info_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/about/contact",
            params={"phone": "+1-555-0100", "terms_accepted": True},
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
