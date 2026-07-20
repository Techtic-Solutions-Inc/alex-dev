from datetime import datetime, timezone

from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, DateTime, String, bindparam, select
from sqlalchemy.orm import Session

from src.models.base import Base
from src.models.mixins import UUIDPrimaryKeyMixin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    def update_password(self, new_password: str) -> None:
        """Hash and store a new password, clearing any active reset token."""
        self.hashed_password = pwd_context.hash(new_password)
        self.password_reset_token = None
        self.password_reset_token_expires_at = None

    @classmethod
    def get_by_reset_token(cls, db: Session, token: str) -> "User | None":
        stmt = select(cls).where(
            cls.password_reset_token == bindparam("reset_token")
        )
        return db.execute(stmt, {"reset_token": token}).scalars().first()

    def is_reset_token_valid(self) -> bool:
        if self.password_reset_token_expires_at is None:
            return False
        expires_at = self.password_reset_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at >= datetime.now(timezone.utc)
