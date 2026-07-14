import pytest
from src.tests.helpers.test_helpers import create_mock_user, setup_test_db


@pytest.fixture(scope='function')
def test_db():
    setup_test_db()


def test_create_mock_user():
    user = create_mock_user(username='mockuser')
    assert user.username == 'mockuser'
    assert user.email == 'testuser@example.com'


def test_setup_test_db(test_db):
    # Add assertions to verify the test database setup
    assert True  # Placeholder for actual assertions
