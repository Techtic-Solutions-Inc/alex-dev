from pathlib import Path

import pytest
from httpx import AsyncClient

from app.core.config import settings
from app.main import app

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def test_required_project_files_exist() -> None:
    expected_paths = [
        _BACKEND_DIR / "pyproject.toml",
        _BACKEND_DIR / "alembic.ini",
        _BACKEND_DIR / "app/main.py",
        _BACKEND_DIR / "app/core/config.py",
        _BACKEND_DIR / "app/db/migrations/env.py",
        _BACKEND_DIR / "app/db/migrations/versions/001_initial_migration.py",
        _BACKEND_DIR / ".env.test",
    ]
    missing = [str(path) for path in expected_paths if not path.exists()]
    assert missing == []


def test_settings_load_test_database_url() -> None:
    assert settings.DATABASE_URL == (
        "postgresql+psycopg2://postgres:1234@localhost:5432/mydb"
    )
    assert settings.JWT_SECRET == "test_secret_key_for_pytest"


def test_fastapi_app_metadata() -> None:
    assert app.title == "Backend API"
    assert app.version == "0.1.0"


@pytest.mark.asyncio
async def test_health_endpoint_registered(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
