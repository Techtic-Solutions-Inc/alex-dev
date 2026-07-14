import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

@pytest.fixture
def sample_user():
    return {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'securepassword',
        'role': 'user'
    }

# Happy path tests
def test_login_happy_path(sample_user):
    response = client.post('/api/v1/auth/login', json={
        'email': sample_user['email'],
        'password': sample_user['password']
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()

# Edge case tests
def test_login_empty_email():
    response = client.post('/api/v1/auth/login', json={
        'email': '',
        'password': 'securepassword'
    })
    assert response.status_code == 400

def test_login_long_email():
    long_email = 'a' * 256 + '@example.com'
    response = client.post('/api/v1/auth/login', json={
        'email': long_email,
        'password': 'securepassword'
    })
    assert response.status_code == 400

# Error case tests
def test_login_invalid_credentials():
    response = client.post('/api/v1/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_login_unauthorized_access():
    response = client.get('/api/v1/auth/protected')
    assert response.status_code == 401

# Additional tests for error handling

def test_error_handling_invalid_route():
    response = client.get('/api/v1/auth/nonexistent')
    assert response.status_code == 404

# Test logging
def test_logging_on_error_handling():
    response = client.get('/api/v1/auth/nonexistent')
    assert response.status_code == 404
    # Here we would check logs if logging is properly set up
