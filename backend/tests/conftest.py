
import os
import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.core.security import create_access_token
from app.dependencies.db import get_db

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_db"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
async def client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def admin_id() -> str:
    return str(uuid.uuid4())

@pytest.fixture
def auth_header(admin_id: str) -> dict[str, str]:
    token = create_access_token({"sub": admin_id, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}
