from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.models.password_reset_token import PasswordResetToken
from src.api.v1.models.user import User
from src.api.v1.schemas.auth import RequestPasswordResetResponse
from src.config import settings
from src.database import get_db
from src.main import app
from src.models.base import Base
from src.services.email_service import EmailService

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

TEST_DATABASE_URL = 'sqlite://'
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def override_get_db(db_session: Session) -> Generator[None, None, None]:
    def _get_test_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def mock_email_service() -> MagicMock:
    return MagicMock(spec=EmailService)


@pytest.fixture
def client(mock_email_service: MagicMock, db_session: Session) -> TestClient:
    from src.api.v1.services import auth_service as auth_service_module
    from src.api.v1.routes import request_password_reset as request_password_reset_module

    original_auth_service = auth_service_module.AuthService

    class TestAuthService(original_auth_service):
        def __init__(self, db: Session) -> None:
            super().__init__(db, email_service=mock_email_service)

    auth_service_module.AuthService = TestAuthService
    request_password_reset_module.AuthService = TestAuthService
    try:
        yield TestClient(app)
    finally:
        auth_service_module.AuthService = original_auth_service
        request_password_reset_module.AuthService = original_auth_service


@pytest.fixture
def registered_user(db_session: Session) -> User:
    user = User(
        email='resetrequest@example.com',
        hashed_password=pwd_context.hash('password123'),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_request_password_reset_success(
    client: TestClient,
    mock_email_service: MagicMock,
    registered_user: User,
    db_session: Session,
) -> None:
    response = client.post(
        '/api/v1/email/reset',
        json={'email': registered_user.email},
    )

    assert response.status_code == 200
    assert response.json() == RequestPasswordResetResponse().model_dump()

    reset_token = (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == registered_user.id)
        .one()
    )
    assert reset_token.token
    assert reset_token.used_at is None
    assert reset_token.expires_at is not None

    mock_email_service.send_password_reset_email.assert_called_once()
    call_args = mock_email_service.send_password_reset_email.call_args
    assert call_args[0][0] == registered_user.email
    reset_link = call_args[0][1]
    assert reset_token.token in reset_link
    assert reset_link.startswith(settings.PASSWORD_RESET_API_URL)


def test_request_password_reset_nonexistent_email(
    client: TestClient,
    mock_email_service: MagicMock,
    db_session: Session,
) -> None:
    response = client.post(
        '/api/v1/email/reset',
        json={'email': 'unknown@example.com'},
    )

    assert response.status_code == 200
    assert response.json() == RequestPasswordResetResponse().model_dump()
    mock_email_service.send_password_reset_email.assert_not_called()
    assert db_session.query(PasswordResetToken).count() == 0
