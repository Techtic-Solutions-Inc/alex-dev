import base64
import json
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.authenticate import get_user_service
from src.config import Settings, get_settings
from src.database import get_db
from src.main import app
from src.models.base import Base
from src.services.auth0_service import Auth0Service
from src.services.user_service import UserService


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        database_url="sqlite://",
        auth0_domain="test.auth0.com",
        auth0_client_id="test-client-id",
        auth0_client_secret="test-client-secret",
        auth0_audience="https://api.example.com",
        dashboard_url="/dashboard",
    )


@pytest.fixture
def db_session(test_settings: Settings) -> Generator[Session, None, None]:
    engine = create_engine(
        test_settings.database_url,
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
def mock_auth0_service() -> MagicMock:
    return MagicMock(spec=Auth0Service)


@pytest.fixture
def user_service(db_session: Session, mock_auth0_service: MagicMock, test_settings: Settings) -> UserService:
    return UserService(db=db_session, auth0_service=mock_auth0_service, settings=test_settings)


@pytest.fixture
def client(db_session: Session, user_service: UserService) -> Generator[TestClient, None, None]:
    get_settings.cache_clear()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_get_user_service() -> UserService:
        return user_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_service] = override_get_user_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def build_id_token(sub: str = "auth0|123") -> str:
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).decode().rstrip("=")
    return f"{header}.{payload}.signature"


def build_auth0_token_response(email: str = "user@example.com") -> dict[str, Any]:
    return {
        "access_token": "test-access-token",
        "token_type": "Bearer",
        "expires_in": 86400,
        "id_token": build_id_token(f"auth0|{email}"),
    }
