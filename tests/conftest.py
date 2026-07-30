from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.middleware.rate_limiting import reset_rate_limiters
from src.models.base import Base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/project_8e8b832f"


@pytest.fixture(scope="session")
def engine():
    return create_engine(DATABASE_URL)


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture
async def client(tables):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture
def mock_auth0_service(mocker):
    mock_class = mocker.patch("src.services.user_service.Auth0Service")
    instance = MagicMock()
    mock_class.return_value = instance
    mock_class.authenticate_user = instance.authenticate
    return mock_class


@pytest.fixture(autouse=True)
def default_auth0_success(mock_auth0_service):
    mock_auth0_service.authenticate_user.return_value = {
        "access_token": "mock_access_token",
        "id_token": "mock_id_token",
        "expires_in": 3600,
    }
    yield


@pytest.fixture(autouse=True)
def reset_rate_limits():
    reset_rate_limiters()
    yield
    reset_rate_limiters()


@pytest_asyncio.fixture
async def test_users(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.execute(text("DELETE FROM users"))
    session.commit()
    session.close()
    yield
