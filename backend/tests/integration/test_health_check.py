from httpx import AsyncClient


async def test_health_check_returns_200(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


async def test_health_check_response_body(client: AsyncClient) -> None:
    response = await client.get("/health")
    data = response.json()
    assert data == {
        "success": True,
        "message": "Service is healthy",
        "data": {"status": "healthy"},
    }


async def test_health_check_does_not_require_auth(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


async def test_health_check_rejects_post(client: AsyncClient) -> None:
    response = await client.post("/health")
    assert response.status_code == 405
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "HTTP_ERROR"
