"""Shared pytest fixtures for backend API and migration tests."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator

import pytest
from httpx import ASGITransport, AsyncClient
from pymongo import MongoClient
from pymongo.database import Database

os.environ.setdefault("APP_ENV", "test")

from app.core.config import settings  # noqa: E402
from app.db.migrations import MIGRATIONS, MigrationRunner  # noqa: E402
from app.main import create_application  # noqa: E402


def _migration_db_name() -> str:
    return os.environ.get("TEST_DB_NAME", settings.DB_NAME)


@pytest.fixture(scope="session")
def mongo_client() -> Iterator[MongoClient]:
    """Connect to the configured MongoDB instance for integration tests."""
    client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5_000)
    client.admin.command("ping")
    yield client
    client.close()


@pytest.fixture
def test_db(mongo_client: MongoClient) -> Iterator[Database]:
    """Provide an isolated, migrated database for each test."""
    db_name = settings.DB_NAME
    mongo_client.drop_database(db_name)
    database = mongo_client[db_name]
    MigrationRunner(database, MIGRATIONS).upgrade()
    yield database
    mongo_client.drop_database(db_name)


@pytest.fixture
def migration_db(mongo_client: MongoClient) -> Iterator[Database]:
    """Provide an isolated database dedicated to migration tests."""
    db_name = _migration_db_name()
    mongo_client.drop_database(db_name)
    database = mongo_client[db_name]
    yield database
    mongo_client.drop_database(db_name)


@pytest.fixture
async def client(test_db: Database, mongo_client: MongoClient) -> AsyncIterator[AsyncClient]:
    """HTTP client wired to the FastAPI app and isolated test database."""
    app = create_application()
    app.state.mongo_client = mongo_client
    app.state.database = test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
