import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_about_success(client: AsyncClient) -> None:
    response = await client.get("/api/about")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "team_members" in body["data"]
    assert "marketing_content" in body["data"]


@pytest.mark.asyncio
async def test_submit_contact_info_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/about/contact",
        json={"phone": "+1-555-0100", "terms_accepted": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["phone"] == "+1-555-0100"
    assert body["data"]["terms_accepted"] is True
