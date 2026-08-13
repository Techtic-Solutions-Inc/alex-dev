from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Announcement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Announcement ORM model."""

    __tablename__ = "announcements"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    highlights: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    privacy_policy_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    terms_of_service_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
