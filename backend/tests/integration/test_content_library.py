import pytest
from httpx import AsyncClient
from tests.conftest import auth_header


@pytest.mark.asyncio
async def test_get_user_details_happy_path(
    async_client: AsyncClient,
    user_token_headers: dict[str, str],
) -> None:
    response = await async_client.get(
        "/api/content-library/user-details",
        headers=user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "name" in data["data"]
    assert "ai_credit_usage" in data["data"]


@pytest.mark.asyncio
async def test_get_user_details_forbidden(
    async_client: AsyncClient,
    user_token_headers: dict[str, str],
    other_user_token_headers: dict[str, str],
) -> None:
    from app.core.security import verify_token

    owner_token = user_token_headers["Authorization"].removeprefix("Bearer ")
    other_token = other_user_token_headers["Authorization"].removeprefix("Bearer ")
    owner_id = verify_token(owner_token)["sub"]
    other_id = verify_token(other_token)["sub"]

    response = await async_client.get(
        "/api/content-library/user-details",
        params={"user_id": other_id},
        headers=auth_header(owner_id),
    )
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "You cannot access another user's details"
