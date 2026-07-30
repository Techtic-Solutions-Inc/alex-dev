import time

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from src.config import Settings
from src.middleware.rate_limiting import RateLimitStrategy, create_rate_limiter, setup_rate_limiting


def create_test_app(settings: Settings) -> FastAPI:
    app = FastAPI()

    @app.get("/test")
    def test_endpoint() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health")
    def health_endpoint() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/custom",
        dependencies=[
            Depends(
                create_rate_limiter(
                    requests=1,
                    window_seconds=60,
                    strategy=RateLimitStrategy.IP,
                )
            )
        ],
    )
    def custom_endpoint() -> dict[str, str]:
        return {"status": "custom"}

    setup_rate_limiting(app, settings)
    return app


@pytest.fixture
def rate_limit_settings() -> Settings:
    return Settings(
        rate_limit_enabled=True,
        rate_limit_requests=2,
        rate_limit_window_seconds=60,
        rate_limit_strategy="ip_and_path",
        rate_limit_excluded_paths=["/health"],
    )


def test_rate_limit_not_exceeded(rate_limit_settings: Settings) -> None:
    app = create_test_app(rate_limit_settings)
    with TestClient(app) as client:
        for _ in range(rate_limit_settings.rate_limit_requests):
            response = client.get("/test")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}


def test_rate_limit_exceeded(rate_limit_settings: Settings) -> None:
    app = create_test_app(rate_limit_settings)
    with TestClient(app) as client:
        for _ in range(rate_limit_settings.rate_limit_requests):
            client.get("/test")

        response = client.get("/test")

        assert response.status_code == 429
        assert response.json()["detail"] == "Rate limit exceeded. Please try again later."
        assert response.headers["Retry-After"] == str(rate_limit_settings.rate_limit_window_seconds)
        assert response.headers["X-RateLimit-Limit"] == str(rate_limit_settings.rate_limit_requests)


def test_rate_limit_reset() -> None:
    settings = Settings(
        rate_limit_enabled=True,
        rate_limit_requests=1,
        rate_limit_window_seconds=1,
        rate_limit_strategy="ip",
        rate_limit_excluded_paths=["/health"],
    )
    app = create_test_app(settings)

    with TestClient(app) as client:
        first_response = client.get("/test")
        assert first_response.status_code == 200

        blocked_response = client.get("/test")
        assert blocked_response.status_code == 429

        time.sleep(1.1)

        reset_response = client.get("/test")
        assert reset_response.status_code == 200


def test_rate_limit_excluded_paths(rate_limit_settings: Settings) -> None:
    app = create_test_app(rate_limit_settings)
    with TestClient(app) as client:
        for _ in range(rate_limit_settings.rate_limit_requests + 5):
            response = client.get("/health")
            assert response.status_code == 200


def test_rate_limit_user_strategy() -> None:
    settings = Settings(
        rate_limit_enabled=True,
        rate_limit_requests=1,
        rate_limit_window_seconds=60,
        rate_limit_strategy="user",
        rate_limit_excluded_paths=["/health"],
    )
    app = create_test_app(settings)

    with TestClient(app) as client:
        first_user_response = client.get("/test", headers={"X-User-Id": "user-1"})
        second_user_response = client.get("/test", headers={"X-User-Id": "user-2"})
        blocked_user_response = client.get("/test", headers={"X-User-Id": "user-1"})

        assert first_user_response.status_code == 200
        assert second_user_response.status_code == 200
        assert blocked_user_response.status_code == 429


def test_rate_limit_disabled() -> None:
    settings = Settings(
        rate_limit_enabled=False,
        rate_limit_requests=1,
        rate_limit_window_seconds=60,
    )
    app = create_test_app(settings)

    with TestClient(app) as client:
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200
