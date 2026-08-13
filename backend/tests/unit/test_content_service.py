import uuid
from unittest.mock import MagicMock

import pytest
from app.exceptions.http_exceptions import ConflictException, NotFoundException
from app.models.content import Content
from app.schemas.content import ContentCreateRequest, ContentUpdateRequest
from app.services.content_service import ContentService


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def content_service(mock_db: MagicMock) -> ContentService:
    return ContentService(mock_db)


@pytest.fixture
def sample_content() -> Content:
    return Content(
        id=uuid.uuid4(),
        caption="Hates to see me coming",
        description="Hates to see me coming",
        phone="+1-555-0100",
        terms_accepted=True,
        privacy_policy=True,
        full_name="Joseph",
    )


def test_create_content_success(
    content_service: ContentService,
    sample_content: Content,
) -> None:
    content_service.repository.get_by_caption = MagicMock(return_value=None)
    content_service.repository.create = MagicMock(return_value=sample_content)
    content_service.analytics.track_event = MagicMock()
    content_service.stripe.record_content_activity = MagicMock()

    payload = ContentCreateRequest(
        caption="Hates to see me coming",
        terms_accepted=True,
        privacy_policy=True,
        phone="+1-555-0100",
        full_name="Joseph",
    )
    result = content_service.create_content(payload, user_id="user-1")

    assert result.caption == sample_content.caption
    assert result.phone == sample_content.phone
    assert result.full_name == "Joseph"
    assert result.link == f"/api/content/{sample_content.id}"
    assert result.error is None
    content_service.repository.create.assert_called_once()
    content_service.analytics.track_event.assert_called_once()
    content_service.stripe.record_content_activity.assert_called_once()


def test_create_content_missing_fields_validation() -> None:
    with pytest.raises(Exception):
        ContentCreateRequest(
            caption="",
            terms_accepted=True,
            privacy_policy=True,
            phone="",
        )


def test_create_content_duplicate_caption(
    content_service: ContentService,
    sample_content: Content,
) -> None:
    content_service.repository.get_by_caption = MagicMock(
        return_value=sample_content,
    )

    payload = ContentCreateRequest(
        caption="Hates to see me coming",
        terms_accepted=True,
        privacy_policy=True,
        phone="+1-555-0100",
    )

    with pytest.raises(ConflictException) as exc_info:
        content_service.create_content(payload)

    assert exc_info.value.code == "CONTENT_CAPTION_ALREADY_EXISTS"


def test_get_content_success(
    content_service: ContentService,
    sample_content: Content,
) -> None:
    content_service.repository.get_by_id = MagicMock(return_value=sample_content)
    content_service.analytics.track_event = MagicMock()
    content_service.stripe.record_content_activity = MagicMock()

    result = content_service.get_content(sample_content.id)

    assert result.id == str(sample_content.id)
    assert result.caption == sample_content.caption
    assert result.description
    assert result.link == f"/api/content/{sample_content.id}"


def test_get_content_not_found(content_service: ContentService) -> None:
    content_service.repository.get_by_id = MagicMock(return_value=None)

    with pytest.raises(NotFoundException) as exc_info:
        content_service.get_content(uuid.uuid4())

    assert exc_info.value.code == "CONTENT_NOT_FOUND"


def test_update_content_success(
    content_service: ContentService,
    sample_content: Content,
) -> None:
    content_service.repository.get_by_id = MagicMock(return_value=sample_content)
    content_service.repository.get_by_caption = MagicMock(return_value=None)
    content_service.repository.update = MagicMock(return_value=sample_content)
    content_service.analytics.track_event = MagicMock()
    content_service.stripe.record_content_activity = MagicMock()

    payload = ContentUpdateRequest(caption="Updated caption")
    result = content_service.update_content(sample_content.id, payload)

    assert result.caption == sample_content.caption
    content_service.repository.update.assert_called_once()


def test_update_content_invalid_empty_caption() -> None:
    with pytest.raises(Exception):
        ContentUpdateRequest(caption="")


def test_update_content_not_found(content_service: ContentService) -> None:
    content_service.repository.get_by_id = MagicMock(return_value=None)

    with pytest.raises(NotFoundException) as exc_info:
        content_service.update_content(
            uuid.uuid4(),
            ContentUpdateRequest(caption="Updated"),
        )

    assert exc_info.value.code == "CONTENT_NOT_FOUND"
