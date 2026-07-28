import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database import Base, get_db
from src.main import app
from src.models.user import User
from src.services.auth_service import create_access_token

DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/test_db'

@pytest.fixture(scope='session')
def db_engine():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
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

@pytest.fixture(scope='function')
def test_users(db_session):
    users = [
        User(email='admin@test.com', hashed_password='hashed_admin', role='admin', is_active=True),
        User(email='user@test.com', hashed_password='hashed_user', role='user', is_active=True),
        User(email='viewer@test.com', hashed_password='hashed_viewer', role='viewer', is_active=True),
        User(email='inactive@test.com', hashed_password='hashed_inactive', role='user', is_active=False),
    ]
    db_session.add_all(users)
    db_session.commit()
    return users

@pytest.fixture(scope='function')
def auth_tokens(test_users):
    return {user.email: create_access_token(user.email) for user in test_users}
