"""Pytest configuration and shared fixtures."""

import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.database import Base, get_db
from src.config.settings import get_settings
from src.main import app

TEST_DATABASE_URL = "sqlite://"


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide an isolated in-memory database session for tests."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI test client with overridden database dependency."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_sendgrid() -> Generator[MagicMock, None, None]:
    """Mock SendGrid client so tests do not call the external API."""
    env = {
        "SENDGRID_API_KEY": "test-sendgrid-key",
        "SENDGRID_FROM_EMAIL": "test@example.com",
    }
    with patch.dict(os.environ, env, clear=False):
        get_settings.cache_clear()
        with patch("src.services.email_service.SendGridAPIClient") as mock_client_cls:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 202
            mock_client.send.return_value = mock_response
            mock_client_cls.return_value = mock_client
            yield mock_client
        get_settings.cache_clear()
