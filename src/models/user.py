from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    auth0_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
