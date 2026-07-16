"""Send transactional email tests."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from src.services.email_service import EmailService

RESET_LINK = 'http://localhost:8000/api/v1/reset-password?token=abc123'


def test_send_reset_email_success(caplog: pytest.LogCaptureFixture) -> None:
    email_service = EmailService(api_key='test-api-key', from_email='noreply@example.com')
    mock_client = MagicMock()
    mock_response = MagicMock(status_code=202)
    mock_client.send.return_value = mock_response

    with caplog.at_level(logging.INFO):
        with patch('src.services.email_service.SendGridAPIClient', return_value=mock_client):
            email_service.send_password_reset_email('user@example.com', RESET_LINK)

    mock_client.send.assert_called_once()
    sent_message = mock_client.send.call_args[0][0]
    assert sent_message.from_email.email == 'noreply@example.com'
    assert sent_message.personalizations[0].tos[0]['email'] == 'user@example.com'
    assert sent_message.subject.subject == 'Password Reset Request'

    message_contents = {content.mime_type: content.content for content in sent_message.contents}
    assert 'Click here to reset your password.' in message_contents['text/html']
    assert RESET_LINK in message_contents['text/html']
    assert 'Click here to reset your password' in message_contents['text/plain']
    assert RESET_LINK in message_contents['text/plain']
    assert 'Password reset email sent to user@example.com' in caplog.text


def test_send_reset_email_failure(caplog: pytest.LogCaptureFixture) -> None:
    email_service = EmailService(api_key='test-api-key', from_email='noreply@example.com')
    mock_client = MagicMock()
    mock_client.send.side_effect = Exception('SendGrid error')

    with caplog.at_level(logging.ERROR):
        with patch('src.services.email_service.SendGridAPIClient', return_value=mock_client):
            with pytest.raises(RuntimeError, match='Failed to send password reset email'):
                email_service.send_password_reset_email('user@example.com', RESET_LINK)

    assert 'Failed to send password reset email to user@example.com' in caplog.text
