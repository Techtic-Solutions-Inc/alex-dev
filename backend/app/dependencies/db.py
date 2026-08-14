from collections.abc import AsyncIterator

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.session import db


async def get_db() -> AsyncIterator[AsyncIOMotorDatabase]:
    """Yield the MongoDB database handle for request-scoped operations."""
    yield db
