
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.api.models.user import User
from src.config.test_database import (
    TestSessionLocal,
    create_test_tables,
    drop_test_tables,
)
from src.utils.password import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create and tear down database tables for the test session."""
    create_test_tables()
    yield
    drop_test_tables()


@pytest.fixture
def client() -> AsyncClient:
    """Return a FastAPI test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


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
def mock_auth0_service():
    """Mock the Auth0 service for authentication."""
    with patch('src.api.services.auth0_service.Auth0AuthenticationService.authenticate', return_value=True):
        yield
