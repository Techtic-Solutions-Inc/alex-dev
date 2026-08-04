from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column

from models.base import Base


class User(MappedAsDataclass, Base):
    """Application user stored in PostgreSQL."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, init=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default=None
    )
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default=None
    )
    mobile_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, default=None
    )
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    profile_picture: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        init=False,
    )
