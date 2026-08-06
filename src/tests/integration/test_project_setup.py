"""Integration tests verifying project setup acceptance criteria."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_folder_structure() -> None:
    expected_folders = [
        "src/api/controllers",
        "src/api/models",
        "src/api/routes",
        "src/api/services",
        "src/config",
        "src/middlewares",
        "src/utils",
        "src/tests",
        "src/migrations",
        "src/public",
        "src/uploads",
    ]
    for folder in expected_folders:
        assert os.path.exists(folder), f"Folder {folder} does not exist"


def test_database_connection() -> None:
    from src.config.database import engine

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.fetchone() == (1,)


def test_jwt_middleware_integration(client: TestClient) -> None:
    response = client.get(
        "/protected-endpoint",
        headers={"Authorization": "Bearer fake_token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_global_error_handler(client: TestClient) -> None:
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_logging_middleware(client: TestClient) -> None:
    with patch("src.middlewares.logging.logger.info") as mock_logger_info:
        response = client.get("/health")
        assert response.status_code == 200
        mock_logger_info.assert_called_with("Request: GET /health - Response: 200")


def test_env_file_exists() -> None:
    assert os.path.exists(".env.example"), ".env.example file does not exist"


def test_cors_configuration(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_openapi_documentation(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "FastAPI Backend"


def test_migrations_setup() -> None:
    assert os.path.exists("src/migrations/env.py"), (
        "Alembic environment file does not exist"
    )
