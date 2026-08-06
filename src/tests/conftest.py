import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from src.config.test_database import TestSessionLocal, create_test_tables, drop_test_tables
from src.utils.password import hash_password
from src.api.models.user import User

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    create_test_tables()
    yield
    drop_test_tables()

@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client

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
        User(username="admin", email="admin@test.com", password_hash=hash_password("TestAdmin123!")),
        User(username="user", email="user@test.com", password_hash=hash_password("TestUser123!")),
        User(username="viewer", email="viewer@test.com", password_hash=hash_password("TestViewer123!")),
        User(username="inactive", email="inactive@test.com", password_hash=hash_password("TestInactive123!"), is_email_verified=False),
    ]
    db_session.bulk_save_objects(users)
    db_session.commit()
    yield users
    for user in users:
        db_session.delete(user)
    db_session.commit()
