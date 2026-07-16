from collections.abc import Generator
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.models.password_reset_token import PasswordResetToken
from src.api.v1.models.user import User
from src.config import settings
from src.database import get_db
from src.main import app
from src.models.base import Base

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
def client(override_get_db: None) -> TestClient:
    return TestClient(app)


@pytest.fixture
def reset_user_and_token(db_session: Session) -> dict[str, str]:
    user = User(
        email='resetuser@example.com',
        hashed_password=pwd_context.hash('oldpassword123'),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token_value = 'valid-reset-token-abc123'
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token_value,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(reset_token)
    db_session.commit()

    return {
        'email': user.email,
        'token': token_value,
        'old_password': 'oldpassword123',
    }


def test_reset_password_success(client: TestClient, reset_user_and_token: dict[str, str], db_session: Session) -> None:
    response = client.post(
        '/api/v1/reset-password',
        json={
            'token': reset_user_and_token['token'],
            'new_password': 'newsecurepassword123',
            'confirm_password': 'newsecurepassword123',
        },
    )

    assert response.status_code == 200
    assert response.json()['message'] == (
        'Your password has been reset successfully! You can now log in.'
    )

    user = db_session.query(User).filter(User.email == reset_user_and_token['email']).one()
    assert pwd_context.verify('newsecurepassword123', user.hashed_password)
    assert not pwd_context.verify('oldpassword123', user.hashed_password)

    reset_token = (
        db_session.query(PasswordResetToken)
        .filter(PasswordResetToken.token == reset_user_and_token['token'])
        .one()
    )
    assert reset_token.used_at is not None


def test_reset_password_invalid_token(client: TestClient) -> None:
    response = client.post(
        '/api/v1/reset-password',
        json={
            'token': 'invalid-token',
            'new_password': 'newsecurepassword123',
            'confirm_password': 'newsecurepassword123',
        },
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid or expired reset link'


def test_reset_password_mismatch(client: TestClient, reset_user_and_token: dict[str, str]) -> None:
    response = client.post(
        '/api/v1/reset-password',
        json={
            'token': reset_user_and_token['token'],
            'new_password': 'newsecurepassword123',
            'confirm_password': 'differentpassword123',
        },
    )

    assert response.status_code == 422


def test_reset_password_redirect_to_page(
    client: TestClient,
    reset_user_and_token: dict[str, str],
) -> None:
    token = reset_user_and_token['token']
    expected_url = f'{settings.PASSWORD_RESET_FRONTEND_URL}?token={token}'

    response = client.get(
        '/api/v1/reset-password',
        params={'token': token},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers['location'] == expected_url


def test_reset_password_redirect_invalid_token(client: TestClient) -> None:
    response = client.get(
        '/api/v1/reset-password',
        params={'token': 'invalid-token'},
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid or expired reset link'
