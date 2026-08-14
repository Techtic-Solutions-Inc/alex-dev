
import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_ENV_TEST = _BACKEND_DIR / ".env.test"


def _load_env_test() -> None:
    """Load .env.test into os.environ before application imports."""
    if not _ENV_TEST.exists():
        return
    for line in _ENV_TEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_env_test()

from app.core.config import settings
from app.core.security import create_refresh_token
from app.db.session import db
from app.main import app


@pytest.fixture(scope="module")
def test_db():
    """Provide the MongoDB database handle configured for testing."""
    yield db


@pytest.fixture(scope="session")
def test_mongo_client() -> AsyncIterator[AsyncIOMotorClient]:
    """Create a dedicated MongoDB client for integration tests."""
    client = AsyncIOMotorClient(settings.TEST_MONGODB_URL)
    yield client
    client.close()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client for API integration tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.fixture
def valid_refresh_token() -> str:
    """Return a valid refresh token for auth endpoint tests."""
    return create_refresh_token({"sub": "test-user-id", "role": "user"})
