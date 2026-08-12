
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_jwt_auth_middleware(client: AsyncClient, mocker):
    mocker.patch("app.middleware.auth.get_current_user", return_value={"sub": "user@test.com"})
    response = await client.get("/protected-endpoint")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logging_middleware(client: AsyncClient, caplog):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "Request: http://test/health - Response: 200" in caplog.text


@pytest.mark.asyncio
async def test_cors_setup(client: AsyncClient):
    response = await client.options("/health")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_rate_limiter_middleware(client: AsyncClient):
    for _ in range(5):
        response = await client.get("/health")
        assert response.status_code == 200
    response = await client.get("/health")
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_error_handling(client: AsyncClient):
    response = await client.get("/non-existent-endpoint")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
