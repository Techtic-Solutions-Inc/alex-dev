
import pytest
from fastapi.testclient import TestClient
from main import app
from src.config.database import engine, Base
from sqlalchemy.orm import sessionmaker

DATABASE_URL_TEST = "postgresql+asyncpg://user:password@localhost/test_dbname"

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def db_session():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
