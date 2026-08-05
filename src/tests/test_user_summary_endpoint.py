
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_user_summary_happy_path(async_client: AsyncClient, db_session):
    # Insert test data
    await db_session.execute("""
        INSERT INTO users (email, is_active) VALUES
        ('active1@test.com', true),
        ('active2@test.com', true),
        ('inactive@test.com', false);
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
async def test_get_user_summary_openapi_documented(async_client: AsyncClient):
    response = await async_client.get("/openapi.json")

    assert response.status_code == 200
    openapi_data = response.json()
    paths = openapi_data.get("paths", {})
    assert "/api/users/summary" in paths
