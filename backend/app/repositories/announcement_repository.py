import uuid
from datetime import date, datetime, time, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.announcement import Announcement


class AnnouncementRepository:
    """Data access layer for announcement records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_announcements(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        filter_date: date | None = None,
    ) -> tuple[list[Announcement], int]:
        """Return paginated announcements ordered by creation date descending."""
        stmt = select(Announcement)
        count_stmt = select(func.count()).select_from(Announcement)

        if filter_date is not None:
            start = datetime.combine(filter_date, time.min, tzinfo=timezone.utc)
            end = datetime.combine(filter_date, time.max, tzinfo=timezone.utc)
            date_filter = Announcement.created_at.between(start, end)
            stmt = stmt.where(date_filter)
            count_stmt = count_stmt.where(date_filter)

        stmt = (
            stmt.order_by(Announcement.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list(self.db.scalars(stmt).all())
        total = self.db.scalar(count_stmt) or 0
        return items, total

    def get_by_id(self, announcement_id: uuid.UUID) -> Announcement | None:
        """Return an announcement by primary key."""
        stmt = select(Announcement).where(Announcement.id == announcement_id)
        return self.db.scalar(stmt)

    def create(self, announcement: Announcement) -> Announcement:
        """Persist a new announcement and return the saved record."""
        self.db.add(announcement)
        self.db.commit()
        self.db.refresh(announcement)
        return announcement

    def update(self, announcement: Announcement) -> Announcement:
        """Persist changes to an existing announcement."""
        self.db.commit()
        self.db.refresh(announcement)
        return announcement

    def delete(self, announcement: Announcement) -> None:
        """Remove an announcement from the database."""
        self.db.delete(announcement)
        self.db.commit()
