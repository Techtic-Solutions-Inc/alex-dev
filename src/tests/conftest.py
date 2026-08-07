
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from src.api.models.user import User
from src.config.test_database import TestSessionLocal, create_test_tables, drop_test_tables
from src.utils.password import hash_password


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
    """Create test users for various roles."""
    users = [
        User(username="admin", first_name="Admin", last_name="User", email="admin@test.com", password_hash=hash_password("TestAdmin123!"), is_active=True),
        User(username="regular", first_name="Regular", last_name="User", email="user@test.com", password_hash=hash_password("TestUser123!"), is_active=True),
        User(username="viewer", first_name="Viewer", last_name="User", email="viewer@test.com", password_hash=hash_password("TestViewer123!"), is_active=True),
        User(username="inactive", first_name="Inactive", last_name="User", email="inactive@test.com", password_hash=hash_password("TestInactive123!"), is_active=False),
        User(username="newuser", first_name="New", last_name="User", email="newuser@test.com", password_hash=hash_password("NewUser123!"), is_active=True)
    ]
    db_session.bulk_save_objects(users)
    db_session.commit()
    yield users
    db_session.query(User).delete()
    db_session.commit()
