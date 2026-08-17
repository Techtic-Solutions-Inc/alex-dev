"""MongoDB client lifecycle and database dependencies."""

from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings


def create_mongo_client() -> MongoClient:
    """Create a client without connecting until a database operation is requested."""
    return MongoClient(
        settings.MONGODB_URL,
        serverSelectionTimeoutMS=5_000,
        connect=False,
    )


async def get_database(request: Request) -> AsyncIterator[Database]:
    """Inject the database attached during application startup."""
    yield request.app.state.database
