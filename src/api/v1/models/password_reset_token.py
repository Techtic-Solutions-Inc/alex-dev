from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKeyMixin
from src.models.types import GUID


class PasswordResetToken(UUIDPrimaryKeyMixin, Base):
    __tablename__ = 'password_reset_tokens'

    user_id = Column(GUID(), ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)

    user = relationship('User', back_populates='password_reset_tokens')

    @property
    def is_valid(self) -> bool:
        return self.used_at is None and self.expires_at > datetime.now(timezone.utc)
