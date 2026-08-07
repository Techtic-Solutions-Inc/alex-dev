
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


@pytest.fixture
def client():
    return TestClient(app)


@patch('src.api.services.user_service.send_confirmation_email')
def test_signup_success(mock_send_email, client):
    mock_send_email.return_value = None  # Mock SendGrid email sending
    response = client.post(
        '/api/auth/signup',
        json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePassword123!',
            'terms_accepted': True
        }
    )
    assert response.status_code == 201
    assert response.json()['success'] is True
    assert response.json()['data']['email'] == 'john.doe@example.com'


def test_signup_missing_first_name(client):
    response = client.post(
        '/api/auth/signup',
        json={
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePassword123!',
            'terms_accepted': True
        }
    )
    assert response.status_code == 400
    assert 'first_name' in response.json()['detail']


def test_signup_invalid_email_format(client):
    response = client.post(
        '/api/auth/signup',
        json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'invalid-email',
            'password': 'SecurePassword123!',
            'terms_accepted': True
        }
    )
    assert response.status_code == 400
    assert 'Invalid email format' in response.json()['detail']


@patch('src.api.services.user_service.create_user_with_confirmation')
def test_signup_duplicate_email(mock_create_user, client):
    mock_create_user.side_effect = Exception('Duplicate email')
    response = client.post(
        '/api/auth/signup',
        json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'duplicate@example.com',
            'password': 'SecurePassword123!',
            'terms_accepted': True
        }
    )
    assert response.status_code == 409
    assert 'Duplicate email' in response.json()['detail']


def test_signup_terms_not_accepted(client):
    response = client.post(
        '/api/auth/signup',
        json={
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePassword123!',
            'terms_accepted': False
        }
    )
    assert response.status_code == 400
    assert 'terms_accepted' in response.json()['detail']
