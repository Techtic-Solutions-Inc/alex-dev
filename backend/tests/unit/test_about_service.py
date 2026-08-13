from unittest.mock import MagicMock

import pytest

from app.exceptions.http_exceptions import BadRequestException
from app.schemas.about import AboutRequest
from app.services.about_service import AboutService


@pytest.fixture
def about_service() -> AboutService:
    return AboutService()


def test_get_about_content_success(about_service: AboutService) -> None:
    about_service.analytics.track_event = MagicMock()

    payload = AboutRequest(phone="+1-555-0100", terms_accepted=True)
    result = about_service.get_about_content(payload, user_id="user-1")

    assert result.id == "about-us"
    assert result.link == "/api/about"
    assert result.phone == "+1-555-0100"
    assert result.terms_accepted is True
    assert result.error is None
    assert len(result.team_members) == 5
    assert result.marketing_content
    assert result.roles

    about_service.analytics.track_event.assert_called_once_with(
        "about_page_viewed",
        user_id="user-1",
        extra_params={
            "page": "about_us",
            "phone": "+1-555-0100",
        },
    )


def test_get_about_content_terms_not_accepted() -> None:
    with pytest.raises(Exception):
        AboutRequest(phone="+1-555-0100", terms_accepted=False)


def test_validate_about_payload_missing_phone(about_service: AboutService) -> None:
    payload = AboutRequest(phone="+1-555-0100", terms_accepted=True)
    data = about_service.get_about_content(payload)
    data.phone = ""

    with pytest.raises(BadRequestException) as exc_info:
        about_service._validate_about_payload(data)

    assert exc_info.value.code == "VALIDATION_ERROR"
    field_names = {item["field"] for item in exc_info.value.details}
    assert "phone" in field_names
