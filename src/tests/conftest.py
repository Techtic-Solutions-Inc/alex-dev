
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from main import app
from src.api.models.user import User
from src.config.test_database import TestSessionLocal, create_test_tables, drop_test_tables
from src.utils.password import hash_password
from src.utils.token import generate_access_token

_env_test = Path(__file__).resolve().parents[2] / ".env.test"
if _env_test.exists():
    for raw_line in _env_test.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


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
def test_users(db_session: Session):
    """Create test users with different roles and states."""
    users = [
        User(email="admin@test.com", password_hash=hash_password("TestAdmin123!"), is_active=True),
        User(email="user@test.com", password_hash=hash_password("TestUser123!"), is_active=True),
        User(email="viewer@test.com", password_hash=hash_password("TestViewer123!"), is_active=True),
        User(email="inactive@test.com", password_hash=hash_password("TestUser123!"), is_active=False),
    ]
    db_session.bulk_save_objects(users)
    db_session.commit()
    yield users
    db_session.query(User).delete()
    db_session.commit()


@pytest.fixture
def auth_tokens(test_users):
    """Generate auth tokens for test users."""
    return {
        "admin": generate_access_token(test_users[0]),
        "user": generate_access_token(test_users[1]),
        "viewer": generate_access_token(test_users[2]),
        "inactive": generate_access_token(test_users[3]),
    }
