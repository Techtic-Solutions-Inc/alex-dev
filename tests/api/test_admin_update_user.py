import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.v1.models.enums import AccountStatus
from src.api.v1.models.user import User
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
def existing_user(db_session: Session) -> User:
    user = User(
        email='admin-update@example.com',
        hashed_password=pwd_context.hash('securepassword123'),
        account_status=AccountStatus.ACTIVE,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_update_user_status_success(
    client: TestClient,
    existing_user: User,
    db_session: Session,
) -> None:
    response = client.post(
        '/api/v1/admin/users/update',
        json={
            'user_id': str(existing_user.id),
            'status': AccountStatus.SUSPENDED.value,
        },
    )

    assert response.status_code == 200
    assert response.json()['message'] == 'User account updated successfully'

    db_session.refresh(existing_user)
    assert existing_user.account_status == AccountStatus.SUSPENDED


def test_update_user_status_invalid_user(client: TestClient) -> None:
    response = client.post(
        '/api/v1/admin/users/update',
        json={
            'user_id': str(uuid.uuid4()),
            'status': AccountStatus.INACTIVE.value,
        },
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'User not found'


def test_update_user_status_invalid_status(
    client: TestClient,
    existing_user: User,
) -> None:
    response = client.post(
        '/api/v1/admin/users/update',
        json={
            'user_id': str(existing_user.id),
            'status': 'invalid_status',
        },
    )

    assert response.status_code == 422
