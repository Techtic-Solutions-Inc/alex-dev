from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Content(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Content details ORM model for the Real Estate Professional module."""

    __tablename__ = "contents"

    caption: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    terms_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    privacy_policy: Mapped[bool] = mapped_column(Boolean, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
