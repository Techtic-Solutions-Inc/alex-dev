from sqlalchemy import Boolean, Column, DateTime, String

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    email_confirmed = Column(Boolean, nullable=False, default=False)
    email_confirmation_token = Column(String(255), nullable=True, index=True)
    email_confirmation_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)
