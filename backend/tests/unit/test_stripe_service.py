from unittest.mock import patch

import pytest
from app.core.config import settings
from app.services.stripe_service import StripeService


def test_record_content_activity_skipped_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "STRIPE_ENABLED", False)
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "")

    service = StripeService()
    assert service.is_configured is False

    with patch("app.services.stripe_service.logger") as mock_logger:
        service.record_content_activity(event_name="content_created")
        mock_logger.debug.assert_called()


def test_record_content_activity_when_configured_without_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "STRIPE_ENABLED", True)
    monkeypatch.setattr(settings, "STRIPE_SECRET_KEY", "sk_test_123")

    service = StripeService()
    assert service.is_configured is True

    # ImportError path is acceptable when the SDK is not installed.
    service.record_content_activity(
        event_name="content_updated",
        caption="Test caption",
        user_id="user-1",
    )
