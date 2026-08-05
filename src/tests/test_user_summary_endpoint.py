
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_summary_happy_path(async_client: AsyncClient, db_session):
    # Insert test data
    await db_session.execute("""
        INSERT INTO users (email, role, is_active) VALUES
        ('user1@test.com', 'user', true),
        ('user2@test.com', 'user', false),
        ('user3@test.com', 'user', true);
    """)
    await db_session.commit()

    response = await async_client.get("/api/users/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 3
    assert data["active_users"] == 2


@pytest.mark.asyncio
async def test_get_user_summary_no_users(async_client: AsyncClient):
    response = await async_client.get("/api/users/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 0
    assert data["active_users"] == 0


@pytest.mark.asyncio
async def test_get_user_summary_documented_in_openapi(async_client: AsyncClient):
    response = await async_client.get("/openapi.json")

    assert response.status_code == 200
    openapi_data = response.json()
    paths = openapi_data.get("paths", {})
    assert "/api/users/summary" in paths
    assert "get" in paths["/api/users/summary"]
