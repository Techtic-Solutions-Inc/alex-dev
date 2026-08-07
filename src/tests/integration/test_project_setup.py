"""Integration tests for project structure and core setup."""

import os
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import text

from main import app
from src.config.database import engine


def test_project_structure() -> None:
    expected_structure = [
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
        "main.py",
    ]
    for path in expected_structure:
        assert os.path.exists(path), f"{path} does not exist"


def test_database_connection() -> None:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.fetchone() == (1,)


def test_jwt_middleware_integration() -> None:
    client = TestClient(app)
    response = client.get("/protected-endpoint")
    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"


def test_global_error_handler() -> None:
    client = TestClient(app)
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_logging_middleware() -> None:
    client = TestClient(app)
    with patch("src.middlewares.logging.logger.info") as mock_logger_info:
        response = client.get("/health")
        assert response.status_code == 200
        mock_logger_info.assert_called_with(
            "Request: GET /health - Response: 200"
        )


def test_env_file_exists() -> None:
    assert os.path.exists(".env.example"), ".env.example file does not exist"


def test_cors_configuration() -> None:
    client = TestClient(app)
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"


def test_openapi_documentation() -> None:
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    assert "FastAPI Backend" in response.text
