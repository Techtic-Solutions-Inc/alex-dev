"""Tests for request logging middleware."""

from fastapi.testclient import TestClient


def test_logging_middleware_adds_request_id_header(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-request-id")


def test_logging_middleware_preserves_supplied_request_id(client: TestClient) -> None:
    request_id = "test-request-id-123"
    response = client.get("/health", headers={"X-Request-ID": request_id})
    assert response.status_code == 200
    assert response.headers.get("x-request-id") == request_id
