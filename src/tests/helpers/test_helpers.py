import uuid
from typing import Any
from src.models import User


def create_mock_user(**kwargs: Any) -> User:
    """Create a mock user instance for testing.

    Args:
        **kwargs: Additional attributes to set on the user.

    Returns:
        User: A user instance with default or overridden attributes.
    """
    user_data = {
        'id': uuid.uuid4(),
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'securepassword',
        **kwargs
    }
    return User(**user_data)


def setup_test_db() -> None:
    """Set up the test database for isolated tests.

    This function should be called before running tests that require a database.
    """
    # Implementation for setting up the test database goes here
    pass
