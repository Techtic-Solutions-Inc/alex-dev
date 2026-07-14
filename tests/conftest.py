import pytest
from src.tests.factories.user_factory import UserFactory

@pytest.fixture
def test_user():
    return UserFactory()

@pytest.fixture
def test_users():
    return [UserFactory() for _ in range(5)]
