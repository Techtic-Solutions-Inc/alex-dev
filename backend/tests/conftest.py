import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings, sync_database_url
from app.core.security import create_access_token
from app.main import app
from app.models.user import User

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_db"

@pytest.fixture(scope="session")
def db_engine() -> Iterator:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def async_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def user_token_headers() -> dict[str, str]:
    token = create_access_token({"sub": "user@test.com", "role": "user"})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def other_user_token_headers() -> dict[str, str]:
    token = create_access_token({"sub": "otheruser@test.com", "role": "user"})
    return {"Authorization": f"Bearer {token}"}
