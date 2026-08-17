import pytest
from httpx import AsyncClient
from pymongo import MongoClient
from app.main import app

@pytest.fixture(scope='module')
def client():
    return AsyncClient(app=app, base_url='http://test')

@pytest.fixture(scope='module')
def mongo_client():
    client = MongoClient('mongodb://localhost:27017')
    yield client
    client.drop_database('test_project')

@pytest.fixture(scope='module')
def test_db(mongo_client):
    db = mongo_client['test_project']
    yield db
    mongo_client.drop_database('test_project')

@pytest.fixture(scope='module')
def setup_users(test_db):
    users = [
        {'email': 'admin@test.com', 'role': 'admin', 'password': 'TestAdmin123!'},
        {'email': 'user@test.com', 'role': 'user', 'password': 'TestUser123!'},
        {'email': 'viewer@test.com', 'role': 'viewer', 'password': 'TestViewer123!'},
        {'email': 'inactive@test.com', 'role': 'user', 'is_active': False},
        {'email': 'newuser@test.com', 'role': 'user', 'password': 'NewUser123!'}
    ]
    test_db['users'].insert_many(users)
    yield
    test_db['users'].delete_many({})