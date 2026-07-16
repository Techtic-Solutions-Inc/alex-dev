import factory
from src.models.user import User
from src.models.admin import Admin


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker('email')
    hashed_password = factory.LazyFunction(lambda: hash_password('securepassword'))


class AdminFactory(factory.Factory):
    class Meta:
        model = Admin

    email = factory.Faker('email')
    hashed_password = factory.LazyFunction(lambda: hash_password('adminpassword'))
