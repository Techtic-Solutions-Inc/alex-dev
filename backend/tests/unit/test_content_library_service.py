import uuid
from unittest.mock import MagicMock

import pytest
from app.exceptions.http_exceptions import ForbiddenException, NotFoundException
from app.models.user import User
from app.services.content_library_service import ContentLibraryService


@pytest.fixture
def service() -> ContentLibraryService:
    svc = ContentLibraryService(db=MagicMock())
    svc.user_repository = MagicMock()
    return svc


def _user(
    *,
    user_id: uuid.UUID | None = None,
    first_name: str = "Jane",
    last_name: str = "Doe",
    ai_credit_usage: int = 10,
) -> User:
    user = User(
        username="jane@example.com",
        email="jane@example.com",
        first_name=first_name,
        last_name=last_name,
        hashed_password="hashed",
    )
    user.id = user_id or uuid.uuid4()
    user.ai_credit_usage = ai_credit_usage
    return user


def test_get_user_details_success(service: ContentLibraryService) -> None:
    user = _user(ai_credit_usage=42)
    service.user_repository.get_by_id.return_value = user

    result = service.get_user_details(str(user.id))

    assert result.user_id == str(user.id)
    assert result.name == "Jane Doe"
    assert result.ai_credit_usage == 42
    service.user_repository.get_by_id.assert_called_once_with(user.id)


def test_get_user_details_matching_requested_id(
    service: ContentLibraryService,
) -> None:
    user = _user()
    service.user_repository.get_by_id.return_value = user

    result = service.get_user_details(
        str(user.id),
        requested_user_id=str(user.id),
    )

    assert result.user_id == str(user.id)


def test_get_user_details_forbidden_other_user(
    service: ContentLibraryService,
) -> None:
    authenticated_id = str(uuid.uuid4())
    other_id = str(uuid.uuid4())

    with pytest.raises(ForbiddenException) as exc_info:
        service.get_user_details(
            authenticated_id,
            requested_user_id=other_id,
        )

    assert exc_info.value.code == "USER_DETAILS_FORBIDDEN"
    assert exc_info.value.status_code == 403
    service.user_repository.get_by_id.assert_not_called()


def test_get_user_details_not_found(service: ContentLibraryService) -> None:
    missing_id = uuid.uuid4()
    service.user_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundException) as exc_info:
        service.get_user_details(str(missing_id))

    assert exc_info.value.code == "USER_NOT_FOUND"
    assert exc_info.value.status_code == 404


def test_get_user_details_invalid_uuid(service: ContentLibraryService) -> None:
    with pytest.raises(NotFoundException) as exc_info:
        service.get_user_details("not-a-uuid")

    assert exc_info.value.code == "USER_NOT_FOUND"
    service.user_repository.get_by_id.assert_not_called()
