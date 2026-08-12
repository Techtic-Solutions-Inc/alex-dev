import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def test_db():
    """Session-scoped fixture for test database setup and teardown."""
    yield


@pytest.fixture
async def client() -> AsyncClient:
    """Provide an async HTTP client bound to the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
