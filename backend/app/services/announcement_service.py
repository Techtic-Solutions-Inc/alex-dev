import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.exceptions.http_exceptions import BadRequestException, NotFoundException
from app.models.announcement import Announcement
from app.repositories.announcement_repository import AnnouncementRepository
from app.schemas.announcement import (
    AnnouncementCreateRequest,
    AnnouncementData,
    AnnouncementUpdateRequest,
)
from app.services.google_analytics_service import GoogleAnalyticsService


class AnnouncementService:
    """Business logic for announcement operations."""

    def __init__(self, db: Session) -> None:
        self.repository = AnnouncementRepository(db)
        self.analytics = GoogleAnalyticsService()

    @staticmethod
    def _to_announcement_data(announcement: Announcement) -> AnnouncementData:
        return AnnouncementData(
            id=str(announcement.id),
            title=announcement.title,
            body=announcement.body,
            highlights=announcement.highlights,
            privacy_policy_accepted=announcement.privacy_policy_accepted,
            terms_of_service_accepted=announcement.terms_of_service_accepted,
        )

    def list_announcements(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        filter_date: date | None = None,
        user_id: str | None = None,
    ) -> tuple[list[AnnouncementData], int]:
        """Return paginated announcements, optionally filtered by date."""
        if page < 1:
            raise BadRequestException(
                message="Page must be at least 1",
                code="VALIDATION_ERROR",
                details=[{"field": "page", "message": "Page must be at least 1"}],
            )
        if limit < 1 or limit > 100:
            raise BadRequestException(
                message="Limit must be between 1 and 100",
                code="VALIDATION_ERROR",
                details=[
                    {
                        "field": "limit",
                        "message": "Limit must be between 1 and 100",
                    }
                ],
            )

        announcements, total = self.repository.list_announcements(
            page=page,
            limit=limit,
            filter_date=filter_date,
        )
        self.analytics.track_event(
            "announcement_list_viewed",
            user_id=user_id,
            extra_params={
                "page": page,
                "limit": limit,
                "filter_date": str(filter_date) if filter_date else None,
            },
        )
        return [self._to_announcement_data(item) for item in announcements], total

    def get_announcement(
        self,
        announcement_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> AnnouncementData:
        """Return a single announcement by ID."""
        announcement = self.repository.get_by_id(announcement_id)
        if announcement is None:
            raise NotFoundException(
                message="Announcement not found",
                code="ANNOUNCEMENT_NOT_FOUND",
            )
        self.analytics.track_event(
            "announcement_viewed",
            title=announcement.title,
            user_id=user_id,
            extra_params={"announcement_id": str(announcement.id)},
        )
        return self._to_announcement_data(announcement)

    def create_announcement(
        self,
        payload: AnnouncementCreateRequest,
        *,
        user_id: str | None = None,
    ) -> AnnouncementData:
        """Create a new announcement."""
        announcement = Announcement(
            title=payload.title,
            body=payload.body,
            highlights=payload.highlights,
            privacy_policy_accepted=payload.privacy_policy_accepted,
            terms_of_service_accepted=payload.terms_of_service_accepted,
        )
        saved = self.repository.create(announcement)
        self.analytics.track_event(
            "announcement_created",
            title=saved.title,
            user_id=user_id,
            extra_params={"announcement_id": str(saved.id)},
        )
        return self._to_announcement_data(saved)

    def update_announcement(
        self,
        announcement_id: uuid.UUID,
        payload: AnnouncementUpdateRequest,
        *,
        user_id: str | None = None,
    ) -> AnnouncementData:
        """Update an existing announcement."""
        announcement = self.repository.get_by_id(announcement_id)
        if announcement is None:
            raise NotFoundException(
                message="Announcement not found",
                code="ANNOUNCEMENT_NOT_FOUND",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException(
                message="At least one field must be provided for update",
                code="VALIDATION_ERROR",
            )

        if "title" in update_data:
            announcement.title = update_data["title"]
        if "body" in update_data:
            announcement.body = update_data["body"]
        if "highlights" in update_data:
            announcement.highlights = update_data["highlights"]
        if "privacy_policy_accepted" in update_data:
            announcement.privacy_policy_accepted = update_data[
                "privacy_policy_accepted"
            ]
        if "terms_of_service_accepted" in update_data:
            announcement.terms_of_service_accepted = update_data[
                "terms_of_service_accepted"
            ]

        saved = self.repository.update(announcement)
        self.analytics.track_event(
            "announcement_updated",
            title=saved.title,
            user_id=user_id,
            extra_params={"announcement_id": str(saved.id)},
        )
        return self._to_announcement_data(saved)

    def delete_announcement(
        self,
        announcement_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> None:
        """Delete an announcement by ID."""
        announcement = self.repository.get_by_id(announcement_id)
        if announcement is None:
            raise NotFoundException(
                message="Announcement not found",
                code="ANNOUNCEMENT_NOT_FOUND",
            )
        title = announcement.title
        self.repository.delete(announcement)
        self.analytics.track_event(
            "announcement_deleted",
            title=title,
            user_id=user_id,
            extra_params={"announcement_id": str(announcement_id)},
        )
