import uuid

from sqlalchemy.orm import Session

from app.exceptions.http_exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.models.content import Content
from app.repositories.content_repository import ContentRepository
from app.schemas.content import (
    ContentCreateRequest,
    ContentData,
    ContentUpdateRequest,
)
from app.services.google_analytics_service import GoogleAnalyticsService
from app.services.stripe_service import StripeService

_DESCRIPTION_MAX_LENGTH = 200


class ContentService:
    """Business logic for content detail operations."""

    def __init__(self, db: Session) -> None:
        self.repository = ContentRepository(db)
        self.analytics = GoogleAnalyticsService()
        self.stripe = StripeService()

    @staticmethod
    def _build_description(caption: str, description: str | None) -> str:
        if description:
            return description.strip()
        stripped = caption.strip()
        if len(stripped) <= _DESCRIPTION_MAX_LENGTH:
            return stripped
        return f"{stripped[:_DESCRIPTION_MAX_LENGTH].rstrip()}..."

    @staticmethod
    def _build_link(content_id: uuid.UUID) -> str:
        return f"/api/content/{content_id}"

    def _to_content_data(self, content: Content) -> ContentData:
        return ContentData(
            id=str(content.id),
            caption=content.caption,
            description=self._build_description(
                content.caption,
                content.description,
            ),
            phone=content.phone,
            terms_accepted=content.terms_accepted,
            privacy_policy=content.privacy_policy,
            full_name=content.full_name,
            link=self._build_link(content.id),
            error=None,
        )

    def get_content(
        self,
        content_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> ContentData:
        """Return content details by ID (public)."""
        content = self.repository.get_by_id(content_id)
        if content is None:
            raise NotFoundException(
                message="Content not found",
                code="CONTENT_NOT_FOUND",
            )
        self.analytics.track_event(
            "content_viewed",
            content_id=content.id,
            caption=content.caption,
            user_id=user_id,
        )
        self.stripe.record_content_activity(
            event_name="content_viewed",
            content_id=content.id,
            caption=content.caption,
            user_id=user_id,
        )
        return self._to_content_data(content)

    def create_content(
        self,
        payload: ContentCreateRequest,
        *,
        user_id: str | None = None,
    ) -> ContentData:
        """Create new content details."""
        if self.repository.get_by_caption(payload.caption):
            raise ConflictException(
                message="Content with this caption already exists",
                code="CONTENT_CAPTION_ALREADY_EXISTS",
            )

        content = Content(
            caption=payload.caption,
            description=self._build_description(
                payload.caption,
                payload.description,
            ),
            phone=payload.phone,
            terms_accepted=payload.terms_accepted,
            privacy_policy=payload.privacy_policy,
            full_name=payload.full_name,
        )
        saved = self.repository.create(content)
        self.analytics.track_event(
            "content_created",
            content_id=saved.id,
            caption=saved.caption,
            user_id=user_id,
        )
        self.stripe.record_content_activity(
            event_name="content_created",
            content_id=saved.id,
            caption=saved.caption,
            user_id=user_id,
        )
        return self._to_content_data(saved)

    def update_content(
        self,
        content_id: uuid.UUID,
        payload: ContentUpdateRequest,
        *,
        user_id: str | None = None,
    ) -> ContentData:
        """Update existing content details."""
        content = self.repository.get_by_id(content_id)
        if content is None:
            raise NotFoundException(
                message="Content not found",
                code="CONTENT_NOT_FOUND",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException(
                message="At least one field must be provided for update",
                code="VALIDATION_ERROR",
            )

        if "caption" in update_data and update_data["caption"] != content.caption:
            existing = self.repository.get_by_caption(update_data["caption"])
            if existing is not None and existing.id != content.id:
                raise ConflictException(
                    message="Content with this caption already exists",
                    code="CONTENT_CAPTION_ALREADY_EXISTS",
                )
            content.caption = update_data["caption"]

        if "description" in update_data:
            content.description = update_data["description"]
        elif "caption" in update_data:
            content.description = self._build_description(
                update_data["caption"],
                content.description,
            )

        if "phone" in update_data:
            content.phone = update_data["phone"]

        if "terms_accepted" in update_data:
            content.terms_accepted = update_data["terms_accepted"]

        if "privacy_policy" in update_data:
            content.privacy_policy = update_data["privacy_policy"]

        if "full_name" in update_data:
            content.full_name = update_data["full_name"]

        saved = self.repository.update(content)
        self.analytics.track_event(
            "content_updated",
            content_id=saved.id,
            caption=saved.caption,
            user_id=user_id,
        )
        self.stripe.record_content_activity(
            event_name="content_updated",
            content_id=saved.id,
            caption=saved.caption,
            user_id=user_id,
        )
        return self._to_content_data(saved)
