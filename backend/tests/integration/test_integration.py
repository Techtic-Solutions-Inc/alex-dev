from httpx import AsyncClient


async def test_health_check_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


async def test_app_openapi_is_available(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Backend API"
    assert "/health" in schema["paths"]


async def test_refresh_token_endpoint(client: AsyncClient, valid_refresh_token: str) -> None:
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": valid_refresh_token},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
