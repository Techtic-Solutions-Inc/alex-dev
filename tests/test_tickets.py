import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def sample_user():
    return {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'securepassword',
        'role': 'user'
    }

@pytest.fixture
def create_user(sample_user):
    response = client.post('/users/', json=sample_user)
    return response.json()


def test_create_ticket_happy_path(create_user):
    response = client.post('/tickets/', json={'title': 'Test Ticket', 'description': 'This is a test ticket.'}, headers={'Authorization': f'Bearer {create_user[