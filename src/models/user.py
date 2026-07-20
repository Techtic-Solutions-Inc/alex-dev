from sqlalchemy import Boolean, Column, DateTime, String

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
