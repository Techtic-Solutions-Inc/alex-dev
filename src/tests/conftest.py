"""Shared pytest fixtures for integration tests."""

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

_env_test = Path(__file__).resolve().parents[2] / ".env.test"
if _env_test.exists():
    for raw_line in _env_test.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())

from main import app  # noqa: E402
from main import limiter  # noqa: E402
from src.api.models.user import User  # noqa: E402
from src.config.test_database import (  # noqa: E402
    TestSessionLocal,
    create_test_tables,
    drop_test_tables,
)
from src.utils.password import hash_password  # noqa: E402


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Clear rate-limit counters so tests do not interfere with each other."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create and tear down database tables for the test session."""
    create_test_tables()
    yield
    drop_test_tables()


@pytest.fixture
def client() -> TestClient:
    """Return a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session() -> Session:
    """Provide a database session bound to the test database."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a disposable user for authentication tests."""
    existing = (
        db_session.query(User).filter(User.username == "testuser").first()
    )
    if existing is not None:
        db_session.delete(existing)
        db_session.commit()

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
