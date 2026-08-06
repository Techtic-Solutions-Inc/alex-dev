"""Shared pytest fixtures and test environment bootstrap."""

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE pairs from an env file without overriding existing vars."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


PROJECT_ROOT = Path(__file__).resolve().parents[2]
_load_env_file(PROJECT_ROOT / ".env.test")
_load_env_file(PROJECT_ROOT / ".env")

from src.config.settings import get_settings

get_settings.cache_clear()

from main import app, limiter
from src.api.models.user import User
from src.config.test_database import (
    TestSessionLocal,
    create_test_tables,
    drop_test_tables,
)
from src.utils.password import hash_password


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> Generator[None, None, None]:
    """Reset rate limit counters between tests."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Generator[None, None, None]:
    """Create application tables once for the test session."""
    create_test_tables()
    yield
    drop_test_tables()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a database session backed by the configured test database."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Persist a known user for authentication tests."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash=hash_password("TestUser123!"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.delete(user)
    db_session.commit()
