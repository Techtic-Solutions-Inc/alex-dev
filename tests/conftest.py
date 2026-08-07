
import os
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from unittest.mock import patch

from main import app
from src.config.test_database import TestSessionLocal, create_test_tables, drop_test_tables
from src.api.models.user import User
from src.utils.password import hash_password

@pytest.fixture(scope='session', autouse=True)
def setup_database():
    create_test_tables()
    yield
    drop_test_tables()

@pytest.fixture
def client() -> AsyncClient:
    return AsyncClient(app=app, base_url='http://test')

@pytest.fixture
def db_session() -> Session:
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_users(db_session: Session):
    users = [
        User(email='admin@test.com', password_hash=hash_password('TestAdmin123!'), role='admin'),
        User(email='user@test.com', password_hash=hash_password('TestUser123!'), role='user'),
        User(email='viewer@test.com', password_hash=hash_password('TestViewer123!'), role='viewer'),
        User(email='inactive@test.com', password_hash=hash_password('TestInactive123!'), role='user', is_active=False),
        # New user is not inserted into the database
    ]
    db_session.bulk_save_objects(users)
    db_session.commit()
    yield users
    db_session.query(User).delete()
    db_session.commit()
