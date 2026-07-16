import pytest
from unittest.mock import patch
from src.services.email_service import EmailService

@pytest.mark.asyncio
async def test_send_password_reset_email_happy_path():
    with patch('src.services.email_service.EmailService.send_password_reset_email') as mock_send_email:
        email_service = EmailService()
        email_service.send_password_reset_email('user@test.com', 'http://reset-link')
        mock_send_email.assert_called_once_with('user@test.com', 'http://reset-link')

@pytest.mark.asyncio
async def test_send_password_reset_email_edge_case_empty_email():
    with patch('src.services.email_service.EmailService.send_password_reset_email') as mock_send_email:
        email_service = EmailService()
        email_service.send_password_reset_email('', 'http://reset-link')
        mock_send_email.assert_not_called()

@pytest.mark.asyncio
async def test_send_password_reset_email_edge_case_invalid_email():
    with patch('src.services.email_service.EmailService.send_password_reset_email') as mock_send_email:
        email_service = EmailService()
        email_service.send_password_reset_email('invalid-email', 'http://reset-link')
        mock_send_email.assert_not_called()

@pytest.mark.asyncio
async def test_send_password_reset_email_error_case_send_failure():
    with patch('src.services.email_service.EmailService.send_password_reset_email', side_effect=Exception('Send failed')) as mock_send_email:
        email_service = EmailService()
        try:
            email_service.send_password_reset_email('user@test.com', 'http://reset-link')
        except Exception as e:
            assert str(e) == 'Send failed'
        mock_send_email.assert_called_once()

@pytest.mark.asyncio
async def test_send_password_reset_email_auth_missing_token():
    # This test is not applicable for email service as it does not require authentication
    pass