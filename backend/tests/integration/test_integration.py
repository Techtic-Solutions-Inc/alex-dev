from httpx import AsyncClient


async def test_app_openapi_is_available(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Backend API"
    assert "/health" in schema["paths"]


async def test_cors_allows_preflight(client: AsyncClient) -> None:
    origin = "http://localhost:3000"
    response = await client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin


async def test_unknown_route_returns_structured_404(client: AsyncClient) -> None:
    response = await client.get("/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body == {
        "success": False,
        "message": "Not Found",
        "error": {"code": "NOT_FOUND", "details": None},
    }
