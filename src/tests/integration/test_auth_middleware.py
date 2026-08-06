import pytest
from fastapi.testclient import TestClient

from main import app
from src.middlewares.auth import get_current_user


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_jwt_auth_middleware(client: TestClient) -> None:
    app.dependency_overrides[get_current_user] = lambda: {"username": "testuser"}
    try:
        response = client.get(
            "/protected-endpoint",
            headers={"Authorization": "Bearer testtoken"},
        )
        assert response.status_code == 200
        assert response.json() == {"user": {"username": "testuser"}}
    finally:
        app.dependency_overrides.clear()
