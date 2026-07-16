import pytest
from fastapi import status


@pytest.mark.parametrize(
    'email, password, expected_status', [
        ('admin@example.com', 'adminpassword', status.HTTP_200_OK),  # Happy path
        ('admin@example.com', '', status.HTTP_400_BAD_REQUEST),  # Edge case: empty password
        ('', 'adminpassword', status.HTTP_400_BAD_REQUEST),  # Edge case: empty email
        ('wrongadmin@example.com', 'adminpassword', status.HTTP_401_UNAUTHORIZED),  # Error case: wrong email
        ('admin@example.com', 'wrongadminpassword', status.HTTP_401_UNAUTHORIZED),  # Error case: wrong password
    ]
)
def test_admin_login(client, sample_admin, email, password, expected_status):
    response = client.post('/admin/login', json={'email': email, 'password': password})
    assert response.status_code == expected_status


def test_admin_login_logging(client, sample_admin, caplog):
    response = client.post('/admin/login', json={'email': 'admin@example.com', 'password': 'adminpassword'})
    assert 'Admin login attempt' in caplog.text
