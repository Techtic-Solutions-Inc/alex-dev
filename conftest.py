"""Shared pytest fixtures and test environment bootstrap."""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

WORKSPACE_ROOT = Path(__file__).resolve().parent
ENV_TEST_PATH = WORKSPACE_ROOT / ".env.test"


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def pytest_configure() -> None:
    _load_env_file(ENV_TEST_PATH)
    os.environ["APP_ENV"] = os.environ.get("ENVIRONMENT", "test")
    os.environ["JWT_SECRET"] = "test_secret_key_for_pytest_must_be_at_least_32_chars"
    os.environ["JWT_EXPIRY"] = "3600"
    os.environ["JWT_REFRESH_EXPIRY"] = "86400"
    os.environ["CORS_ORIGINS"] = "http://localhost:3000"
    os.environ["RATE_LIMIT_REQUESTS"] = "100"
    os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "60"

    from app.core.config import get_settings

    get_settings.cache_clear()


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def mongodb_client():
    from pymongo import MongoClient

    mongo_url = os.environ.get("TEST_MONGODB_URL") or os.environ.get(
        "MONGODB_URL", "mongodb://localhost:27017"
    )
    db_name = os.environ.get("TEST_DB_NAME") or os.environ.get("DB_NAME", "mydatabase_test")

    mongo = MongoClient(mongo_url)
    yield mongo, db_name
    mongo.drop_database(db_name)
    mongo.close()
