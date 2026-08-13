import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.content_template import ContentTemplate

_ACTIVE_STATUS = "active"


class ContentTemplateRepository:
    """Data access layer for Content Library template records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(
        self,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ContentTemplate], int]:
        """Return paginated active content templates ordered by title."""
        base_filter = ContentTemplate.status == _ACTIVE_STATUS
        stmt = (
            select(ContentTemplate)
            .where(base_filter)
            .order_by(ContentTemplate.title.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        count_stmt = (
            select(func.count())
            .select_from(ContentTemplate)
            .where(base_filter)
        )
        items = list(self.db.scalars(stmt).all())
        total = self.db.scalar(count_stmt) or 0
        return items, total

    def search_active(
        self,
        query: str,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ContentTemplate], int]:
        """Search active templates by title or description (case-insensitive)."""
        pattern = f"%{query}%"
        base_filter = ContentTemplate.status == _ACTIVE_STATUS
        search_filter = or_(
            ContentTemplate.title.ilike(pattern),
            ContentTemplate.description.ilike(pattern),
        )
        combined = base_filter & search_filter

        stmt = (
            select(ContentTemplate)
            .where(combined)
            .order_by(ContentTemplate.title.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        count_stmt = (
            select(func.count())
            .select_from(ContentTemplate)
            .where(combined)
        )
        items = list(self.db.scalars(stmt).all())
        total = self.db.scalar(count_stmt) or 0
        return items, total

    def get_by_id(self, template_id: uuid.UUID) -> ContentTemplate | None:
        """Return a content template by primary key."""
        stmt = select(ContentTemplate).where(ContentTemplate.id == template_id)
        return self.db.scalar(stmt)

    def get_by_title(self, title: str) -> ContentTemplate | None:
        """Return a content template matching the given title (case-insensitive)."""
        stmt = select(ContentTemplate).where(
            func.lower(ContentTemplate.title) == title.lower()
        )
        return self.db.scalar(stmt)

    def create(self, template: ContentTemplate) -> ContentTemplate:
        """Persist a new content template and return the saved record."""
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def update(self, template: ContentTemplate) -> ContentTemplate:
        """Persist changes to an existing content template."""
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete(self, template: ContentTemplate) -> None:
        """Remove a content template from the database."""
        self.db.delete(template)
        self.db.commit()
