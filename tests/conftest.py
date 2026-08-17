import pytest
from pymongo import MongoClient
from unittest.mock import patch

@pytest.fixture(scope='session')
def mongodb_client():
    client = MongoClient('mongodb://localhost:27017/test_db')
    yield client
    client.drop_database('test_db')
    client.close()

@pytest.fixture(scope='session')
def test_users(mongodb_client):
    users = [
        {'email': 'admin@test.com', 'role': 'admin', 'password': 'TestAdmin123!'},
        {'email': 'user@test.com', 'role': 'user', 'password': 'TestUser123!'},
        {'email': 'viewer@test.com', 'role': 'viewer', 'password': 'TestViewer123!'},
        {'email': 'inactive@test.com', 'role': 'user', 'is_active': False},
        {'email': 'newuser@test.com', 'role': 'user', 'password': 'NewUser123!'}
    ]
    db = mongodb_client['test_db']
    db.users.insert_many(users)
    return users

@pytest.fixture(scope='function')
def mock_jwt_service(mocker):
    return mocker.patch('src.common.utils.token_util.JwtService')
