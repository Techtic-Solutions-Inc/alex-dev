import uuid
from unittest.mock import patch

import pytest
from app.core.config import settings
from app.services.google_analytics_service import GoogleAnalyticsService


def test_track_event_skipped_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GOOGLE_ANALYTICS_ENABLED", False)
    monkeypatch.setattr(settings, "GOOGLE_ANALYTICS_MEASUREMENT_ID", "")
    monkeypatch.setattr(settings, "GOOGLE_ANALYTICS_API_SECRET", "")

    service = GoogleAnalyticsService()
    assert service.is_configured is False

    with patch("urllib.request.urlopen") as mock_urlopen:
        service.track_event("blog_post_viewed", blog_id=uuid.uuid4())
        mock_urlopen.assert_not_called()


def test_track_event_sent_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "GOOGLE_ANALYTICS_ENABLED", True)
    monkeypatch.setattr(settings, "GOOGLE_ANALYTICS_MEASUREMENT_ID", "G-TEST123")
    monkeypatch.setattr(settings, "GOOGLE_ANALYTICS_API_SECRET", "secret-key")

    service = GoogleAnalyticsService()
    assert service.is_configured is True

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.status = 204
        service.track_event(
            "blog_post_created",
            blog_id=uuid.uuid4(),
            title="Test",
            user_id="user-1",
        )
        mock_urlopen.assert_called_once()
