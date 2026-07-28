
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, get_db
from src.services.user_service import UserService, get_user_service
from unittest.mock import patch

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_db"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def admin_user_token():
    return "mocked-admin-token"

@pytest.fixture(scope="function")
def mock_auth0(mocker):
    mocker.patch("src.services.auth0.Auth0", return_value=MagicMock())
