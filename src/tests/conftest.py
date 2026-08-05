
import asyncio
import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env.test", override=True)
load_dotenv(PROJECT_ROOT / ".env", override=False)
os.environ.setdefault("AUTO_MIGRATE", "false")

from api.middlewares.rate_limiter import limiter
from config.database import get_db_session, normalize_database_url
from config.migrations import ensure_migrations_at_head
from main import app

DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL") or os.getenv("DB_URL"))
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured for tests")

limiter.enabled = False

@pytest_asyncio.fixture(scope="function", autouse=True)
async def _reset_rate_limiter() -> AsyncGenerator[None, None]:
    limiter.reset()
    yield

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    await asyncio.to_thread(ensure_migrations_at_head)

    engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        await session.execute(text("DELETE FROM users"))
        await session.commit()

    async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with session_factory() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
