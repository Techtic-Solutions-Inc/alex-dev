from sqlalchemy import Column, String

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKeyMixin


class Admin(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "admins"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
