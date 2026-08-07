"""Integration tests for JWT authentication middleware."""

from fastapi.testclient import TestClient

from main import app
from src.middlewares.auth import get_current_user


def test_jwt_auth_middleware_dependency_override() -> None:
    client = TestClient(app)
    app.dependency_overrides[get_current_user] = lambda: "test-user-id"
    try:
        response = client.get(
            "/protected-endpoint",
            headers={"Authorization": "Bearer testtoken"},
        )
        assert response.status_code == 200
        assert response.json() == {"user": "test-user-id"}
    finally:
        app.dependency_overrides.clear()
