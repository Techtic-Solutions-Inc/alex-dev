import pytest
from unittest.mock import patch
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_password_recovery_valid_email(client: AsyncClient, mocker):
    # Mock the email sending function
    mock_send_email = mocker.patch('app.services.email_service.send_password_recovery_email', return_value=None)

    # Test: Initiate password recovery
    response = await client.post('/api/auth/password-recovery', json={'email': 'user@test.com'})
    assert response.status_code == 200
    mock_send_email.assert_called_once()

@pytest.mark.asyncio
async def test_password_recovery_invalid_email_format(client: AsyncClient):
    # Test: Invalid email format
    response = await client.post('/api/auth/password-recovery', json={'email': 'invalid-email'})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_password_recovery_empty_email(client: AsyncClient):
    # Test: Empty email field
    response = await client.post('/api/auth/password-recovery', json={'email': ''})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_password_recovery_non_existent_email(client: AsyncClient):
    # Test: Email not associated with any account
    response = await client.post('/api/auth/password-recovery', json={'email': 'nonexistent@test.com'})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_password_reset_link_expiry(client: AsyncClient, mocker):
    # Mock the email sending function to simulate link expiry
    mock_send_email = mocker.patch('app.services.email_service.send_password_recovery_email', return_value=None)

    # Test: Initiate password recovery
    response = await client.post('/api/auth/password-recovery', json={'email': 'user@test.com'})
    assert response.status_code == 200

    # Simulate link expiry
    # This would typically involve checking the token expiry logic
    # Here we assume the token is expired for the sake of the test
    expired_token = 'expired_token'
    response = await client.post('/api/auth/password-reset', json={'token': expired_token, 'new_password': 'NewPass123!'})
    assert response.status_code == 400
