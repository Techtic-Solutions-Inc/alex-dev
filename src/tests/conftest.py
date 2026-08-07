
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from src.config.test_database import TestSessionLocal, create_test_tables, drop_test_tables
from src.api.models.user import User
from src.utils.password import hash_password

_env_test = Path(__file__).resolve().parents[2] / '.env.test'
if _env_test.exists():
    for raw_line in _env_test.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        key, _, value = line.partition('=')
        os.environ.setdefault(key.strip(), value.strip())


@pytest.fixture(scope='session', autouse=True)
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
        {'email': 'admin@test.com', 'role': 'admin', 'password': 'TestAdmin123!'},
        {'email': 'user@test.com', 'role': 'user', 'password': 'TestUser123!'},
        {'email': 'viewer@test.com', 'role': 'viewer', 'password': 'TestViewer123!'},
        {'email': 'inactive@test.com', 'role': 'user', 'is_active': False},
        {'email': 'newuser@test.com', 'role': 'user', 'password': 'NewUser123!'}
    ]
    for user_data in users:
        user = User(
            email=user_data['email'],
            role=user_data['role'],
            password_hash=hash_password(user_data['password']),
            is_active=user_data.get('is_active', True)
        )
        db_session.add(user)
    db_session.commit()
    yield users
    db_session.query(User).delete()
    db_session.commit()
