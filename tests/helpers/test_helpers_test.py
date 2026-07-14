import pytest
from src.tests.helpers.test_helpers import create_test_user, mock_external_service


def test_create_test_user():
    user = create_test_user(username='testuser', email='testuser@example.com', password='securepassword')
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'
    assert user.password == 'securepassword'


def test_create_test_user_with_empty_username():
    with pytest.raises(ValueError, match='Username cannot be empty'):
        create_test_user(username='', email='testuser@example.com', password='securepassword')


def test_create_test_user_with_invalid_email():
    with pytest.raises(ValueError, match='Invalid email format'):
        create_test_user(username='testuser', email='invalid-email', password='securepassword')


def test_mock_external_service():
    response = mock_external_service('some_endpoint')
    assert response['status'] == 'success'


def test_mock_external_service_with_invalid_endpoint():
    with pytest.raises(ValueError, match='Invalid endpoint provided'):
        mock_external_service('')
