import pytest
from src.tests.factories.user_factory import UserFactory


def test_user_factory_creates_user():
    user = UserFactory()
    assert user.username.startswith('testuser')
    assert user.email.endswith('@example.com')
    assert user.password == 'securepassword'
