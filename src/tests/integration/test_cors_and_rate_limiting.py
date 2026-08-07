"""Integration tests for CORS and rate limiting middleware."""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_cors_configuration(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"


def test_rate_limiting(client: TestClient) -> None:
    for _ in range(10):
        response = client.get("/openapi.json")
        assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}
