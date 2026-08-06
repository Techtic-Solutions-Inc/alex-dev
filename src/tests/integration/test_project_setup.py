
import os
import pytest
from fastapi.testclient import TestClient
from main import app


def test_project_structure():
    expected_structure = [
        'src/api/controllers',
        'src/api/models',
        'src/api/routes',
        'src/api/services',
        'src/config',
        'src/middlewares',
        'src/utils',
        'src/tests',
        'src/migrations',
        'src/public',
        'src/uploads',
        'main.py'
    ]
    for path in expected_structure:
        assert os.path.exists(path), f"{path} does not exist"


def test_database_connection():
    from src.config.database import engine
    with engine.connect() as connection:
        result = connection.execute("SELECT 1")
        assert result.fetchone() == (1,)


def test_jwt_middleware_integration():
    client = TestClient(app)
    response = client.get("/protected-endpoint")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_global_error_handler():
    client = TestClient(app)
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_logging_middleware():
    from loguru import logger
    client = TestClient(app)
    with logger.catch() as log:
        client.get("/health")
    assert any("Request: GET /health" in str(record) for record in log.records)


def test_env_file_exists():
    assert os.path.exists('.env.example'), ".env.example file does not exist"


def test_cors_configuration():
    client = TestClient(app)
    response = client.options("/health")
    assert response.headers["access-control-allow-origin"] == "*"


def test_openapi_documentation():
    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
    assert "FastAPI Backend" in response.text
