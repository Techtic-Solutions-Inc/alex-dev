import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.blog_detail import BlogDetail


class BlogDetailRepository:
    """Data access layer for blog details submission records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, detail_id: uuid.UUID) -> BlogDetail | None:
        """Return a blog details submission by primary key."""
        stmt = select(BlogDetail).where(BlogDetail.id == detail_id)
        return self.db.scalar(stmt)

    def create(self, detail: BlogDetail) -> BlogDetail:
        """Persist a new blog details submission."""
        self.db.add(detail)
        self.db.commit()
        self.db.refresh(detail)
        return detail

    def update(self, detail: BlogDetail) -> BlogDetail:
        """Persist changes to an existing blog details submission."""
        self.db.commit()
        self.db.refresh(detail)
        return detail

    def delete(self, detail: BlogDetail) -> None:
        """Remove a blog details submission from the database."""
        self.db.delete(detail)
        self.db.commit()
