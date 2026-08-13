from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """User ORM model."""

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    mobile_number: Mapped[str] = mapped_column(
        String(50), nullable=False, default="", server_default=""
    )
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    address_street: Mapped[str] = mapped_column(
        String(255), nullable=False, default="", server_default=""
    )
    address_city: Mapped[str] = mapped_column(
        String(100), nullable=False, default="", server_default=""
    )
    address_state: Mapped[str] = mapped_column(
        String(100), nullable=False, default="", server_default=""
    )
    address_zip: Mapped[str] = mapped_column(
        String(20), nullable=False, default="", server_default=""
    )
    address_country: Mapped[str] = mapped_column(
        String(100), nullable=False, default="", server_default=""
    )
    time_zone: Mapped[str] = mapped_column(
        String(50), nullable=False, default="", server_default=""
    )
    ai_credit_usage: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
