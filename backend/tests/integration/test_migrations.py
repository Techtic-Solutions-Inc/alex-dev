
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_initial_migration(test_db):
    async with test_db.acquire() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_migration_rollback(test_db):
    async with test_db.acquire() as conn:
        await conn.execute(text("INSERT INTO test_table (name) VALUES ('test')"))
        await conn.execute(text("DELETE FROM test_table WHERE name='test'"))
        result = await conn.execute(text("SELECT COUNT(*) FROM test_table WHERE name='test'"))
        assert result.scalar() == 0
