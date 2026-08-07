
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch('src.api.services.auth_service.authenticate_user')
def test_login_success(mock_authenticate_user, client):
    mock_authenticate_user.return_value = {
        'id': '123',
        'email': 'user@example.com',
        'access_token': 'fake-jwt-token',
        'token_type': 'bearer',
        'expires_in': 3600
    }
    response = client.post(
        '/api/auth/login',
        json={
            'email': 'user@example.com',
            'password': 'securePassword123'
        }
    )
    assert response.status_code == 201
    assert response.json()['success'] is True
    assert 'access_token' in response.json()['data']


def test_login_empty_fields(client):
    response = client.post(
        '/api/auth/login',
        json={
            'email': '',
            'password': ''
        }
    )
    assert response.status_code == 400
    assert 'email' in response.json()['detail']
    assert 'password' in response.json()['detail']


@patch('src.api.services.auth_service.authenticate_user')
def test_login_incorrect_password(mock_authenticate_user, client):
    mock_authenticate_user.side_effect = Exception('Incorrect password')
    response = client.post(
        '/api/auth/login',
        json={
            'email': 'user@example.com',
            'password': 'wrongPassword'
        }
    )
    assert response.status_code == 409
    assert 'Incorrect password' in response.json()['detail']


def test_access_protected_route_without_token(client):
    response = client.get('/api/protected-route')
    assert response.status_code == 403
    assert 'Not authenticated' in response.json()['detail']
