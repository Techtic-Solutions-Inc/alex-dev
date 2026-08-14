from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
db: AsyncIOMotorDatabase = client[settings.DB_NAME]

# Aerich uses Tortoise ORM for migration metadata. Tortoise does not support MongoDB
# URLs directly, so migration state is tracked in a local SQLite database while
# application data is stored in MongoDB via Motor above.
TORTOISE_ORM = {
    "connections": {
        "default": settings.AERICH_DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}


async def ping_database() -> None:
    """Verify MongoDB connectivity by issuing a server ping."""
    await db.command("ping")


async def close_database_client() -> None:
    """Close the MongoDB client connection."""
    client.close()
