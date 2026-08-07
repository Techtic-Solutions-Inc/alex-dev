
import pytest
from httpx import AsyncClient
from unittest.mock import patch

from main import app
from src.api.services.email_service import EmailService

@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, mocker):
    mock_send_email = mocker.patch.object(EmailService, 'send_confirmation_email', return_value=None)
    response = await client.post('/api/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'SecurePassword123!',
        'terms_accepted': True
    })
    assert response.status_code == 201
    assert response.json()['data']['email'] == 'john.doe@example.com'
    mock_send_email.assert_called_once()

@pytest.mark.asyncio
async def test_signup_missing_first_name(client: AsyncClient):
    response = await client.post('/api/auth/signup', json={
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'SecurePassword123!',
        'terms_accepted': True
    })
    assert response.status_code == 400
    assert response.json()['message'] == 'First name is required.'

@pytest.mark.asyncio
async def test_signup_invalid_email_format(client: AsyncClient):
    response = await client.post('/api/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'invalid-email',
        'password': 'SecurePassword123!',
        'terms_accepted': True
    })
    assert response.status_code == 400
    assert response.json()['message'] == 'Invalid email format.'

@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, db_session):
    # Assume a user with this email already exists in the test database
    response = await client.post('/api/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'existing@example.com',
        'password': 'SecurePassword123!',
        'terms_accepted': True
    })
    assert response.status_code == 409
    assert response.json()['message'] == 'Email already exists.'

@pytest.mark.asyncio
async def test_signup_terms_not_accepted(client: AsyncClient):
    response = await client.post('/api/auth/signup', json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'password': 'SecurePassword123!',
        'terms_accepted': False
    })
    assert response.status_code == 400
    assert response.json()['message'] == 'Terms must be accepted.'
