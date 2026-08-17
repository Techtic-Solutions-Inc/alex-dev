"""Integration test for MongoDB connectivity using test environment settings."""

import os

import pytest
from pymongo import MongoClient


def test_mongodb_connection() -> None:
    mongo_url = os.environ.get("TEST_MONGODB_URL") or os.environ.get(
        "MONGODB_URL", "mongodb://localhost:27017"
    )
    client = MongoClient(mongo_url)
    try:
        response = client.admin.command("ping")
    except Exception as exc:
        pytest.fail(f"MongoDB connection failed: {exc}")
    finally:
        client.close()

    assert response["ok"] == 1


def test_mongodb_read_write_round_trip(mongodb_client) -> None:
    client, db_name = mongodb_client
    db = client[db_name]
    collection = db["health_checks"]
    collection.insert_one({"status": "UP"})
    stored = collection.find_one({"status": "UP"})
    assert stored is not None
    assert stored["status"] == "UP"
