from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BlogDetail(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User-submitted blog details contact form record."""

    __tablename__ = "blog_details"

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    privacy_policy_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    terms_of_service_accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
