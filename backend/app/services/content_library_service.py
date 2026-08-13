import uuid

from sqlalchemy.orm import Session

from app.exceptions.http_exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.models.content_template import ContentTemplate
from app.models.user import User
from app.repositories.content_template_repository import ContentTemplateRepository
from app.repositories.user_repository import UserRepository
from app.schemas.content_library import (
    ContentTemplateCreateRequest,
    ContentTemplateData,
    ContentTemplateUpdateRequest,
    UserDetailsData,
)

_VALID_STATUSES = frozenset({"active", "inactive"})
_MIN_SEARCH_QUERY_LENGTH = 1
_MAX_SEARCH_QUERY_LENGTH = 255


class ContentLibraryService:
    """Business logic for Content Library operations."""

    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)
        self.template_repository = ContentTemplateRepository(db)

    @staticmethod
    def _to_template_data(template: ContentTemplate) -> ContentTemplateData:
        return ContentTemplateData(
            id=str(template.id),
            title=template.title,
            description=template.description,
            status=template.status,  # type: ignore[arg-type]
        )

    @staticmethod
    def _validate_pagination(page: int, limit: int) -> None:
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

    @staticmethod
    def _validate_search_query(query: str) -> str:
        stripped = query.strip()
        if len(stripped) < _MIN_SEARCH_QUERY_LENGTH:
            raise BadRequestException(
                message="Search query is required",
                code="VALIDATION_ERROR",
                details=[
                    {
                        "field": "q",
                        "message": "Search query must not be empty",
                    }
                ],
            )
        if len(stripped) > _MAX_SEARCH_QUERY_LENGTH:
            raise BadRequestException(
                message="Search query is too long",
                code="VALIDATION_ERROR",
                details=[
                    {
                        "field": "q",
                        "message": (
                            f"Search query must be at most "
                            f"{_MAX_SEARCH_QUERY_LENGTH} characters"
                        ),
                    }
                ],
            )
        return stripped

    @staticmethod
    def _validate_status(status: str, *, field: str = "status") -> None:
        if status not in _VALID_STATUSES:
            raise BadRequestException(
                message="Validation error",
                code="VALIDATION_ERROR",
                details=[
                    {
                        "field": field,
                        "message": "Status must be 'active' or 'inactive'",
                    }
                ],
            )

    def list_content_templates(
        self,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ContentTemplateData], int]:
        """Return paginated active content templates (public)."""
        self._validate_pagination(page, limit)
        templates, total = self.template_repository.list_active(page=page, limit=limit)
        return [self._to_template_data(item) for item in templates], total

    def search_content_templates(
        self,
        query: str,
        *,
        page: int = 1,
        limit: int = 20,
        user_id: str | None = None,
    ) -> tuple[list[ContentTemplateData], int]:
        """Search active content templates by title or description."""
        validated_query = self._validate_search_query(query)
        self._validate_pagination(page, limit)
        templates, total = self.template_repository.search_active(
            validated_query,
            page=page,
            limit=limit,
        )
        return [self._to_template_data(item) for item in templates], total

    def get_content_template(
        self,
        template_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> ContentTemplateData:
        """Return a single content template by ID."""
        template = self.template_repository.get_by_id(template_id)
        if template is None:
            raise NotFoundException(
                message="Content template not found",
                code="CONTENT_TEMPLATE_NOT_FOUND",
            )
        return self._to_template_data(template)

    def create_content_template(
        self,
        payload: ContentTemplateCreateRequest,
        *,
        user_id: str | None = None,
    ) -> ContentTemplateData:
        """Create a new content template."""
        self._validate_status(payload.status)
        existing = self.template_repository.get_by_title(payload.title)
        if existing is not None:
            raise ConflictException(
                message="A content template with this title already exists",
                code="CONTENT_TEMPLATE_TITLE_ALREADY_EXISTS",
            )

        template = ContentTemplate(
            title=payload.title,
            description=payload.description,
            status=payload.status,
        )
        saved = self.template_repository.create(template)
        return self._to_template_data(saved)

    def update_content_template(
        self,
        template_id: uuid.UUID,
        payload: ContentTemplateUpdateRequest,
        *,
        user_id: str | None = None,
    ) -> ContentTemplateData:
        """Update an existing content template."""
        template = self.template_repository.get_by_id(template_id)
        if template is None:
            raise NotFoundException(
                message="Content template not found",
                code="CONTENT_TEMPLATE_NOT_FOUND",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException(
                message="At least one field must be provided for update",
                code="VALIDATION_ERROR",
            )

        if "title" in update_data:
            new_title = update_data["title"]
            existing = self.template_repository.get_by_title(new_title)
            if existing is not None and existing.id != template.id:
                raise ConflictException(
                    message="A content template with this title already exists",
                    code="CONTENT_TEMPLATE_TITLE_ALREADY_EXISTS",
                )
            template.title = new_title
        if "description" in update_data:
            template.description = update_data["description"]
        if "status" in update_data:
            self._validate_status(update_data["status"])
            template.status = update_data["status"]

        saved = self.template_repository.update(template)
        return self._to_template_data(saved)

    def delete_content_template(
        self,
        template_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> None:
        """Delete a content template by ID."""
        template = self.template_repository.get_by_id(template_id)
        if template is None:
            raise NotFoundException(
                message="Content template not found",
                code="CONTENT_TEMPLATE_NOT_FOUND",
            )
        self.template_repository.delete(template)

    def get_user_details(
        self,
        authenticated_user_id: str,
        *,
        requested_user_id: str | None = None,
    ) -> UserDetailsData:
        """
        Return Content Library details for the authenticated user.

        If ``requested_user_id`` is provided and does not match the
        authenticated user, raise 403 so callers cannot inspect other users.
        """
        if requested_user_id is not None and str(requested_user_id).strip():
            if str(requested_user_id).strip() != str(authenticated_user_id):
                raise ForbiddenException(
                    message="You cannot access another user's details",
                    code="USER_DETAILS_FORBIDDEN",
                )

        user = self._get_user_or_404(authenticated_user_id)
        return UserDetailsData.from_user(user)

    def _get_user_or_404(self, user_id: str) -> User:
        try:
            parsed_id = uuid.UUID(str(user_id))
        except ValueError as exc:
            raise NotFoundException(
                message="User not found",
                code="USER_NOT_FOUND",
            ) from exc

        user = self.user_repository.get_by_id(parsed_id)
        if user is None:
            raise NotFoundException(
                message="User not found",
                code="USER_NOT_FOUND",
            )
        return user
