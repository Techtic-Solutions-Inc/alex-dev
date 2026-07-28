from collections.abc import Generator
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.deps import get_auth_service, get_db
from src.config import Settings
from src.database import Base
from src.main import app
from src.services.auth_service import AuthService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="sqlite://",
        auth0_domain="example.auth0.com",
        auth0_client_id="test-client-id",
        auth0_client_secret="test-client-secret",
        auth0_audience="https://api.example.com",
        dashboard_url="/dashboard",
    )


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_http_client() -> MagicMock:
    return MagicMock(spec=httpx.Client)


@pytest.fixture
def auth_service(settings: Settings, mock_http_client: MagicMock) -> AuthService:
    return AuthService(settings=settings, http_client=mock_http_client)


@pytest.fixture
def client(db_session: Session, auth_service: AuthService) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_auth_service() -> AuthService:
        return auth_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_auth_service] = override_get_auth_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
