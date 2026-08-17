import pytest
from pymongo import MongoClient
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope='session')
def test_client():
    client = TestClient(app)
    yield client

@pytest.fixture(scope='session')
def mongo_client():
    client = MongoClient('mongodb://localhost:27017/test_db')
    yield client
    client.drop_database('test_db')

@pytest.fixture(scope='function', autouse=True)
def setup_db(mongo_client):
    db = mongo_client['test_db']
    yield db
    for collection in db.list_collection_names():
        db.drop_collection(collection)

@pytest.fixture(scope='function')
def create_test_users(setup_db):
    users = [
        {'email': 'admin@test.com', 'role': 'admin', 'password': 'TestAdmin123!', 'is_active': True},
        {'email': 'user@test.com', 'role': 'user', 'password': 'TestUser123!', 'is_active': True},
        {'email': 'viewer@test.com', 'role': 'viewer', 'password': 'TestViewer123!', 'is_active': True},
        {'email': 'inactive@test.com', 'role': 'user', 'password': 'TestInactive123!', 'is_active': False},
        {'email': 'newuser@test.com', 'role': 'user', 'password': 'NewUser123!', 'is_active': True}
    ]
    setup_db['users'].insert_many(users)
    return users
