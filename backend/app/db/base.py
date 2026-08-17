"""SQLAlchemy declarative base and common model mixins."""

from uuid import UUID, uuid4

from sqlalchemy import Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for every persisted model."""


class UUIDPrimaryKeyMixin:
    """Provide UUID primary keys consistently across SQLAlchemy models."""

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
