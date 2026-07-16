import pytest
from fastapi import status


@pytest.mark.parametrize(
    'email, password, expected_status', [
        ('testuser@example.com', 'securepassword', status.HTTP_200_OK),  # Happy path
        ('testuser@example.com', '', status.HTTP_400_BAD_REQUEST),  # Edge case: empty password
        ('', 'securepassword', status.HTTP_400_BAD_REQUEST),  # Edge case: empty email
        ('wronguser@example.com', 'securepassword', status.HTTP_401_UNAUTHORIZED),  # Error case: wrong email
        ('testuser@example.com', 'wrongpassword', status.HTTP_401_UNAUTHORIZED),  # Error case: wrong password
    ]
)
def test_login(client, sample_user, email, password, expected_status):
    response = client.post('/login', json={'email': email, 'password': password})
    assert response.status_code == expected_status


def test_login_logging(client, sample_user, caplog):
    response = client.post('/login', json={'email': 'testuser@example.com', 'password': 'securepassword'})
    assert 'Login attempt' in caplog.text
