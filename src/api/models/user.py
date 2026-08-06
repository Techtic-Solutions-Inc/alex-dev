"""User database model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.api.models.base import BaseModelMixin
from src.config.database import Base


class User(BaseModelMixin, Base):
    """Application user with authentication credentials."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
