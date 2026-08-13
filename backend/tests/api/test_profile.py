import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_profile(
    client: AsyncClient,
    user_token_headers: dict[str, str],
) -> None:
    response = await client.get("/api/profile", headers=user_token_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Profile retrieved successfully"
    assert "first_name" in body["data"]
    assert "last_name" in body["data"]
    assert "email" in body["data"]


@pytest.mark.asyncio
async def test_update_profile(
    client: AsyncClient,
    user_token_headers: dict[str, str],
) -> None:
    response = await client.put(
        "/api/profile",
        json={
            "first_name": "New",
            "last_name": "Name",
            "email": "newemail@example.com",
            "mobile_number": "1234567890",
            "bio": "Updated bio",
            "address": {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "country": "USA",
            },
            "time_zone": "GMT-4",
        },
        headers=user_token_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["first_name"] == "New"
    assert body["data"]["email"] == "newemail@example.com"


@pytest.mark.asyncio
async def test_update_profile_unauthenticated(client: AsyncClient) -> None:
    response = await client.put(
        "/api/profile",
        json={"first_name": "Jane", "last_name": "Doe"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
