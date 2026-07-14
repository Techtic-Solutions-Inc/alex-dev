import factory
from src.models import User


class UserFactory(factory.Factory):
    """Factory for creating user instances for tests."""
    class Meta:
        model = User

    id = factory.LazyFunction(factory.uuid4)
    username = factory.Sequence(lambda n: f'testuser{n}')
    email = factory.Sequence(lambda n: f'testuser{n}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'securepassword')
