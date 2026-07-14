import pytest
from src.tests.factories.user_factory import UserFactory


def test_user_factory_creates_user():
    user = UserFactory()
    assert user.username.startswith('testuser')
    assert user.email.endswith('@example.com')
    assert user.password == 'securepassword'


def test_user_factory_creates_user_with_max_length_username():
    user = UserFactory(username='a' * 256)
    assert len(user.username) <= 255


def test_user_factory_creates_user_with_empty_email():
    with pytest.raises(ValueError, match='Email cannot be empty'):
        UserFactory(email='')


def test_user_factory_creates_user_with_invalid_email_format():
    with pytest.raises(ValueError, match='Invalid email format'):
        UserFactory(email='invalid-email')
