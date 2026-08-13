import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data access layer for user records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return a user matching the given UUID primary key."""
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)

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

    def update(self, user: User) -> User:
        """Persist changes to an existing user and return the refreshed record."""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, hashed_password: str) -> User:
        """Update the user's hashed password and persist the change."""
        user.hashed_password = hashed_password
        return self.update(user)
