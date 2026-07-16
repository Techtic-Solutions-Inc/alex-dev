import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base, get_db
from src.main import app

DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/test_db'

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='session', autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope='function')
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope='function')
async def async_client():
    async with AsyncClient(app=app, base_url='http://test') as client:
        yield client

@pytest.fixture(scope='function')
def existing_user_email(db_session):
    # Create a user and return the email
    user = User(email='user@test.com', hashed_password='hashed_password')
    db_session.add(user)
    db_session.commit()
    return user.email

@pytest.fixture(scope='function')
def valid_reset_token(db_session):
    # Create a valid reset token and return it
    user = User(email='user@test.com', hashed_password='hashed_password')
    db_session.add(user)
    db_session.commit()
    token = PasswordResetToken(user_id=user.id, token='valid-token', expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    db_session.add(token)
    db_session.commit()
    return token.token

@pytest.fixture(scope='function')
def admin_token():
    # Return a dummy admin token
    return 'dummy_admin_token'