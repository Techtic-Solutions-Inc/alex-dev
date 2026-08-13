import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.content import Content


class ContentRepository:
    """Data access layer for content detail records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, content_id: uuid.UUID) -> Content | None:
        """Return content details by primary key."""
        stmt = select(Content).where(Content.id == content_id)
        return self.db.scalar(stmt)

    def get_by_caption(self, caption: str) -> Content | None:
        """Return content matching the given caption (case-insensitive)."""
        stmt = select(Content).where(func.lower(Content.caption) == caption.lower())
        return self.db.scalar(stmt)

    def create(self, content: Content) -> Content:
        """Persist a new content record and return the saved entity."""
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    def update(self, content: Content) -> Content:
        """Persist changes to an existing content record."""
        self.db.commit()
        self.db.refresh(content)
        return content
