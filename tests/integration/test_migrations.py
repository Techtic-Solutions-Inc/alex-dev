import pytest
from pymongo import MongoClient

@pytest.fixture(scope='module')
def mongo_client():
    client = MongoClient('mongodb://localhost:27017')
    yield client
    client.drop_database('test_project_migrations')

@pytest.fixture(scope='module')
def test_db(mongo_client):
    db = mongo_client['test_project_migrations']
    yield db
    mongo_client.drop_database('test_project_migrations')

@pytest.mark.asyncio
async def test_migration_setup(test_db):
    # Assuming a function `run_migrations` exists to apply migrations
    from app.db.migrations import run_migrations
    await run_migrations()
    migration_collection = test_db['_migrations']
    assert migration_collection.count_documents({}) > 0

@pytest.mark.asyncio
async def test_initial_migration(test_db):
    # Assuming a function `run_migrations` exists to apply migrations
    from app.db.migrations import run_migrations
    await run_migrations()
    # Verify initial schema setup
    assert 'users' in test_db.list_collection_names()

@pytest.mark.asyncio
async def test_rollback_capability(test_db):
    from app.db.migrations import downgrade
    # Apply initial migration
    await downgrade('0001_initial_schema')
    # Verify rollback
    assert 'users' not in test_db.list_collection_names()