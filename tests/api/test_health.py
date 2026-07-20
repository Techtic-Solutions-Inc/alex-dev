import pytest
from fastapi.testclient import TestClient

from src.api.v1.router import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_check_status_code(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body(client: TestClient) -> None:
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
