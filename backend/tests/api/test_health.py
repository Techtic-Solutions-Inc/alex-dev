"""Integration tests for the public health endpoint."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_standard_success_envelope() -> None:
    """Health checks must be public and return the documented availability state."""
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "Service is operational.",
        "data": {"status": "UP"},
    }


def test_health_check_is_available_under_api_v1() -> None:
    """Versioned API clients receive the identical health contract."""
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "UP"
