"""Tests for OpenAPI / Swagger documentation exposure."""

from fastapi.testclient import TestClient


def test_openapi_document_is_available(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["title"] == "Backend API"
    assert "/health" in payload["paths"]
    assert "/api/v1/health" in payload["paths"]
    assert "/api/v1/auth/login" in payload["paths"]


def test_swagger_ui_is_available(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
