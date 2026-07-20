import pytest
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import get_db
from src.main import app
from src.models.base import Base
from src.models.user import User
from src.services.auth import hash_password

VALID_RESET_TOKEN = "valid-reset-token-xyz789"
EXPIRED_RESET_TOKEN = "expired-reset-token-abc123"


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def user_with_valid_reset_token(db_session):
    user = User(
        email="user@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token=VALID_RESET_TOKEN,
        password_reset_token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def user_with_expired_reset_token(db_session):
    user = User(
        email="expired@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token=EXPIRED_RESET_TOKEN,
        password_reset_token_expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
