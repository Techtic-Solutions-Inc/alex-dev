from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.models.base import Base
from src.services.auth0_service import Auth0Service

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_db"

@pytest.fixture(scope="session")
def engine():
    return create_engine(DATABASE_URL)


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
async def client(tables):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_auth0_service(mocker):
    mock = mocker.patch("src.services.auth0_service.Auth0Service")
    mock.return_value = MagicMock(spec=Auth0Service)
    return mock


@pytest.fixture
async def test_users(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute("""
    INSERT INTO users (email, role, password, is_active) VALUES
    ('admin@test.com', 'admin', 'TestAdmin123!', true),
    ('user@test.com', 'user', 'TestUser123!', true),
    ('viewer@test.com', 'viewer', 'TestViewer123!', true),
    ('inactive@test.com', 'user', 'TestUser123!', false),
    ('newuser@test.com', 'user', 'NewUser123!', true);
    """)
    session.commit()
    yield
    session.execute("DELETE FROM users;")
    session.commit()
    session.close()
