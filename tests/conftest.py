from collections.abc import Generator
from unittest.mock import MagicMock

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.config import Settings, get_settings
from src.database import Base, get_db
from src.main import app
from src.services.user_service import UserService, get_user_service


@pytest.fixture
def settings() -> Settings:
    return Settings(
        database_url="sqlite://",
        auth0_domain="example.auth0.com",
        auth0_client_id="test-client-id",
        auth0_client_secret="test-client-secret",
        auth0_audience="https://api.example.com",
        dashboard_redirect_url="/dashboard",
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
def user_service(settings: Settings, mock_http_client: MagicMock) -> UserService:
    return UserService(settings=settings, http_client=mock_http_client)


@pytest.fixture
def client(
    db_session: Session,
    user_service: UserService,
    settings: Settings,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_user_service() -> UserService:
        return user_service

    def override_get_settings() -> Settings:
        return settings

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_service] = override_get_user_service
    app.dependency_overrides[get_settings] = override_get_settings

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
