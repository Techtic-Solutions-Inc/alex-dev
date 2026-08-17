"""Tests for CORS headers and rate limiting middleware."""

import os

import pytest
from fastapi.testclient import TestClient


def test_cors_allows_configured_origin(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_rate_limiter_returns_429_with_standard_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")

    from app.core.config import get_settings
    from app.main import create_app

    get_settings.cache_clear()
    limited_app = create_app()

    with TestClient(limited_app) as limited_client:
        assert limited_client.get("/health").status_code == 200
        assert limited_client.get("/health").status_code == 200
        blocked = limited_client.get("/health")

    get_settings.cache_clear()

    assert blocked.status_code == 429
    assert blocked.json() == {
        "success": False,
        "message": "Too many requests. Please try again shortly.",
        "error": {"code": "RATE_LIMIT_EXCEEDED", "details": None},
    }
    assert blocked.headers.get("retry-after") is not None
