
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base

from src.main import app

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture()
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture()
async def test_users(db_session):
    # Insert test users into the database
    users = [
        {"email": "admin@test.com", "role": "admin", "password": "TestAdmin123!"},
        {"email": "user@test.com", "role": "user", "password": "TestUser123!"},
        {"email": "viewer@test.com", "role": "viewer", "password": "TestViewer123!"},
        {"email": "inactive@test.com", "role": "user", "is_active": False},
        {"email": "newuser@test.com", "role": "user", "password": "NewUser123!"}
    ]
    for user in users:
        db_session.add(User(**user))
    await db_session.commit()
    yield users
    await db_session.rollback()
