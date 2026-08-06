"""Integration tests for application components."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from main import app
from src.config.database import engine
from src.config.settings import get_settings


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client."""
    return TestClient(app)


def test_health_check_integration(client: TestClient) -> None:
    """Integration test for the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_database_connection_configuration() -> None:
    """Verify test database URL is configured."""
    settings = get_settings()
    assert settings.database_url_test is not None
    assert settings.database_url_test.startswith(("postgresql", "sqlite"))


def test_database_connection() -> None:
    """Verify database connectivity when PostgreSQL is available."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone() == (1,)
    except OperationalError:
        pytest.skip("PostgreSQL test database is not available.")


def test_primary_database_connection() -> None:
    """Verify primary database connectivity when PostgreSQL is available."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.fetchone() == (1,)
    except OperationalError:
        pytest.skip("PostgreSQL database is not available.")
