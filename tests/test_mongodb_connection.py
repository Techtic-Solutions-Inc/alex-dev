import pytest
from pymongo import MongoClient

@pytest.mark.order(2)
def test_mongodb_connection():
    client = MongoClient('mongodb://localhost:27017/')
    try:
        # Attempt to connect to the database
        client.admin.command('ping')
    except Exception as e:
        pytest.fail(f"MongoDB connection failed: {e}")
    finally:
        client.close()
