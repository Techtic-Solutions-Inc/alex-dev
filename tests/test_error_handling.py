"""Tests for centralized HTTP exception handling."""

from fastapi.testclient import TestClient

from app.exceptions.http_exceptions import AppHTTPException


def test_app_http_exception_fields() -> None:
    exc = AppHTTPException(400, "BAD_REQUEST", "Error occurred", {"field": ["invalid"]})
    assert exc.status_code == 400
    assert exc.code == "BAD_REQUEST"
    assert exc.message == "Error occurred"
    assert exc.details == {"field": ["invalid"]}


def test_not_found_returns_standard_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "message": "The requested resource was not found.",
        "error": {"code": "RESOURCE_NOT_FOUND", "details": None},
    }


def test_validation_error_returns_standard_error_envelope(client: TestClient) -> None:
    response = client.post("/api/v1/auth/login", json={"username": "", "password": ""})
    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["message"] == "One or more fields are invalid."
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(payload["error"]["details"], dict)
