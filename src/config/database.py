import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.environment import get_pool_max_overflow, get_pool_size, is_testing


def normalize_database_url(url: str | None) -> str | None:
    """Convert sync PostgreSQL URLs to the async driver used by the app."""
    if not url:
        return None
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def _build_engine_kwargs() -> dict:
    kwargs: dict = {
        "pool_size": get_pool_size(),
        "max_overflow": get_pool_max_overflow(),
        "pool_pre_ping": True,
    }
    if is_testing():
        kwargs["pool_size"] = 2
        kwargs["max_overflow"] = 0
    pool_recycle = os.getenv("DB_POOL_RECYCLE")
    if pool_recycle:
        kwargs["pool_recycle"] = int(pool_recycle)
    echo = os.getenv("DB_ECHO", "").lower() in {"1", "true", "yes"}
    kwargs["echo"] = echo
    return kwargs


DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL") or os.getenv("DB_URL"))

engine = (
    create_async_engine(DATABASE_URL, **_build_engine_kwargs())
    if DATABASE_URL
    else None
)
async_session_factory = (
    async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    if engine is not None
    else None
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session."""
    if async_session_factory is None:
        raise RuntimeError("DATABASE_URL is not configured")

    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
