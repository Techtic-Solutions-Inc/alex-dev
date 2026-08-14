
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_jwt_auth(client: AsyncClient, valid_refresh_token: str):
    headers = {"Authorization": f"Bearer {valid_refresh_token}"}
    response = await client.get("/api/v1/protected-endpoint", headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_jwt_auth_missing_token(client: AsyncClient):
    response = await client.get("/api/v1/protected-endpoint")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jwt_auth_invalid_token(client: AsyncClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/api/v1/protected-endpoint", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cors_configuration(client: AsyncClient):
    response = await client.options("/api/v1/health")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_logging_middleware(client: AsyncClient, caplog):
    with caplog.at_level("INFO"):
        await client.get("/api/v1/health")
    assert any("Request: GET /api/v1/health" in message for message in caplog.messages)
