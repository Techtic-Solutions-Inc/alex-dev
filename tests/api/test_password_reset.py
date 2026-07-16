import pytest
from fastapi import status


@pytest.mark.parametrize(
    'token, expected_message', [
        ('valid_token', 'Password reset link is valid.'),  # Happy path
        ('expired_token', 'This link has expired. Please request a new password reset link.'),  # Edge case: expired token
        ('', 'This link has expired. Please request a new password reset link.'),  # Edge case: empty token
    ]
)
def test_handle_expired_password_reset_token(client, token, expected_message):
    response = client.post('/reset-password', json={'token': token})
    assert response.json()['message'] == expected_message


def test_no_sensitive_info_exposed(client):
    response = client.post('/reset-password', json={'token': 'expired_token'})
    assert 'expired_token' not in response.text
