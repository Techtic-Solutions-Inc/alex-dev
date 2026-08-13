import uuid

from sqlalchemy.orm import Session

from app.exceptions.http_exceptions import ForbiddenException, NotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.content_library import UserDetailsData


class ContentLibraryService:
    """Business logic for Content Library user-details operations."""

    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

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
