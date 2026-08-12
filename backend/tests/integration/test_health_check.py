from httpx import AsyncClient


async def test_health_check_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Service is healthy"
    assert data["data"]["status"] == "healthy"
