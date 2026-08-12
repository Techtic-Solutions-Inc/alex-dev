
import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

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

from alembic import command
from alembic.config import Config
from app.core.config import settings, sync_database_url
from app.main import app


@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    engine = create_engine(sync_database_url(settings.DATABASE_URL), pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    cfg = Config(str(_BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "app/db/migrations"))
    cfg.set_main_option("sqlalchemy.url", sync_database_url(settings.DATABASE_URL))
    return cfg


@pytest.fixture
def db_session(db_engine: Engine, alembic_config: Config) -> Iterator[Session]:
    command.upgrade(alembic_config, "head")
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
