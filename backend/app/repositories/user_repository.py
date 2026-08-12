from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data access layer for user records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Return a user matching the given email (case-insensitive)."""
        stmt = select(User).where(User.email.ilike(email))
        return self.db.scalar(stmt)

    def create(self, user: User) -> User:
        """Persist a new user and return the saved record."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
