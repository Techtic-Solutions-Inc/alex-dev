
import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.config.database import Base, get_db
from src.main import app

TEST_DATABASE_URL = "sqlite://"

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
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
    env = {
        "SENDGRID_API_KEY": "test-sendgrid-key",
        "SENDGRID_FROM_EMAIL": "test@example.com",
    }
    with patch.dict(os.environ, env, clear=False):
        with patch("src.utils.email.send_confirmation_email") as mock_send_email:
            yield mock_send_email
