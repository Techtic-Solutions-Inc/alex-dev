import pytest
from fastapi import status


@pytest.mark.parametrize(
    'email, password, expected_status', [
        ('newuser@example.com', 'StrongPassword123!', status.HTTP_201_CREATED),  # Happy path
        ('', 'StrongPassword123!', status.HTTP_400_BAD_REQUEST),  # Edge case: empty email
        ('newuser@example.com', '', status.HTTP_400_BAD_REQUEST),  # Edge case: empty password
        ('existinguser@example.com', 'StrongPassword123!', status.HTTP_409_CONFLICT),  # Error case: email already in use
    ]
)
def test_user_registration(client, email, password, expected_status):
    response = client.post('/auth/register', json={'email': email, 'password': password})
    assert response.status_code == expected_status


def test_registration_sends_confirmation_email(client, sample_user):
    response = client.post('/auth/register', json={'email': 'newuser@example.com', 'password': 'StrongPassword123!'})
    assert 'Confirmation email sent' in response.text
