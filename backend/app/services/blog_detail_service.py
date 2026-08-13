import uuid

from sqlalchemy.orm import Session

from app.exceptions.http_exceptions import BadRequestException, NotFoundException
from app.models.blog_detail import BlogDetail
from app.repositories.blog_detail_repository import BlogDetailRepository
from app.schemas.blog_details import (
    BlogDetailsGetData,
    BlogDetailsHeading,
    BlogDetailsPageContent,
    BlogDetailsSection,
    BlogDetailsSubmissionData,
    BlogDetailsSubmitRequest,
    BlogDetailsUpdateRequest,
)
from app.services.google_analytics_service import GoogleAnalyticsService

_BLOG_DETAILS_LINK = "/api/blog/details"

_BLOG_DETAILS_CONTENT = (
    "Lorem Ipsum has been the industry's standard dummy text ever since "
    "the 1500s, when an unknown printer took a galley of type and "
    "scrambled it to make a type specimen book."
)

_BLOG_DETAILS_HEADINGS: tuple[tuple[str, str, int], ...] = (
    ("main-title", "Blog Details", 1),
    ("post-title", "Hates to see me coming", 2),
)

_BLOG_DETAILS_SECTIONS: tuple[tuple[str, str], ...] = (
    (
        "Overview",
        "Discover insights and updates from the Agentwise team on real estate "
        "marketing and technology.",
    ),
    (
        "Mobile App Development",
        "Learn how our mobile-first approach helps agents stay connected "
        "with clients on the go.",
    ),
)

_ADDITIONAL_INFO = (
    "Fill out the form below with your contact information and message "
    "to get in touch about this blog post."
)


class BlogDetailService:
    """Business logic for Blog Details page content and submissions."""

    def __init__(self, db: Session) -> None:
        self.repository = BlogDetailRepository(db)
        self.analytics = GoogleAnalyticsService()

    @staticmethod
    def _build_page_content() -> BlogDetailsPageContent:
        return BlogDetailsPageContent(
            headings=[
                BlogDetailsHeading(id=heading_id, text=text, level=level)
                for heading_id, text, level in _BLOG_DETAILS_HEADINGS
            ],
            content=_BLOG_DETAILS_CONTENT,
            sections=[
                BlogDetailsSection(heading=heading, text=text)
                for heading, text in _BLOG_DETAILS_SECTIONS
            ],
            additional_info=_ADDITIONAL_INFO,
        )

    @staticmethod
    def _to_submission_data(detail: BlogDetail) -> BlogDetailsSubmissionData:
        return BlogDetailsSubmissionData(
            id=str(detail.id),
            first_name=detail.first_name,
            last_name=detail.last_name,
            email=detail.email,
            phone_number=detail.phone_number,
            message=detail.message,
            privacy_policy_accepted=detail.privacy_policy_accepted,
            terms_of_service_accepted=detail.terms_of_service_accepted,
        )

    def get_blog_details(self, *, user_id: str | None = None) -> BlogDetailsGetData:
        """Return Blog Details page content (public)."""
        self.analytics.track_event(
            "blog_details_viewed",
            user_id=user_id,
        )
        return BlogDetailsGetData(
            page=self._build_page_content(),
            link=_BLOG_DETAILS_LINK,
        )

    def create_blog_details(
        self,
        payload: BlogDetailsSubmitRequest,
        *,
        user_id: str | None = None,
    ) -> BlogDetailsSubmissionData:
        """Create a new blog details submission."""
        detail = BlogDetail(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email),
            phone_number=payload.phone_number,
            message=payload.message,
            privacy_policy_accepted=payload.privacy_policy_accepted,
            terms_of_service_accepted=payload.terms_of_service_accepted,
        )
        saved = self.repository.create(detail)
        self.analytics.track_event(
            "blog_details_submitted",
            user_id=user_id,
            extra_params={"detail_id": str(saved.id)},
        )
        return self._to_submission_data(saved)

    def update_blog_details(
        self,
        detail_id: uuid.UUID,
        payload: BlogDetailsUpdateRequest,
        *,
        user_id: str | None = None,
    ) -> BlogDetailsSubmissionData:
        """Update an existing blog details submission."""
        detail = self.repository.get_by_id(detail_id)
        if detail is None:
            raise NotFoundException(
                message="Blog details submission not found",
                code="BLOG_DETAILS_NOT_FOUND",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException(
                message="At least one field must be provided for update",
                code="VALIDATION_ERROR",
            )

        if "first_name" in update_data:
            detail.first_name = update_data["first_name"]
        if "last_name" in update_data:
            detail.last_name = update_data["last_name"]
        if "email" in update_data:
            detail.email = str(update_data["email"])
        if "phone_number" in update_data:
            detail.phone_number = update_data["phone_number"]
        if "message" in update_data:
            detail.message = update_data["message"]
        if "privacy_policy_accepted" in update_data:
            detail.privacy_policy_accepted = update_data["privacy_policy_accepted"]
        if "terms_of_service_accepted" in update_data:
            detail.terms_of_service_accepted = update_data["terms_of_service_accepted"]

        saved = self.repository.update(detail)
        self.analytics.track_event(
            "blog_details_updated",
            user_id=user_id,
            extra_params={"detail_id": str(saved.id)},
        )
        return self._to_submission_data(saved)

    def delete_blog_details(
        self,
        detail_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> None:
        """Delete a blog details submission by ID."""
        detail = self.repository.get_by_id(detail_id)
        if detail is None:
            raise NotFoundException(
                message="Blog details submission not found",
                code="BLOG_DETAILS_NOT_FOUND",
            )
        self.repository.delete(detail)
        self.analytics.track_event(
            "blog_details_deleted",
            user_id=user_id,
            extra_params={"detail_id": str(detail_id)},
        )
