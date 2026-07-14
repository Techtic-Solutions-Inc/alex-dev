from sqlalchemy import Column, String
from src.models.base import Base
from src.models.mixins import UUIDPrimaryKeyMixin

class User(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'users'
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
