import json
import uuid
from typing import Any
from urllib import error, request

from loguru import logger

from app.core.config import settings


class GoogleAnalyticsService:
    """Send interaction events to Google Analytics 4."""

    _MEASUREMENT_URL = "https://www.google-analytics.com/mp/collect"

    def __init__(self) -> None:
        self._measurement_id = settings.GOOGLE_ANALYTICS_MEASUREMENT_ID
        self._api_secret = settings.GOOGLE_ANALYTICS_API_SECRET
        self._enabled = settings.GOOGLE_ANALYTICS_ENABLED

    @property
    def is_configured(self) -> bool:
        return bool(self._enabled and self._measurement_id and self._api_secret)

    def track_event(
        self,
        event_name: str,
        *,
        blog_id: uuid.UUID | None = None,
        title: str | None = None,
        content_id: uuid.UUID | None = None,
        caption: str | None = None,
        user_id: str | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> None:
        """Track an interaction event via the GA4 Measurement Protocol."""
        if not self.is_configured:
            logger.debug(
                "Google Analytics not configured; skipping event {}",
                event_name,
            )
            return

        params: dict[str, str] = {"engagement_time_msec": "100"}
        if blog_id is not None:
            params["blog_id"] = str(blog_id)
        if title is not None:
            params["blog_title"] = title
        if content_id is not None:
            params["content_id"] = str(content_id)
        if caption is not None:
            params["content_caption"] = caption
        if user_id is not None:
            params["user_id"] = user_id
        if extra_params:
            for key, value in extra_params.items():
                if value is not None:
                    params[key] = str(value)

        payload = {
            "client_id": user_id or str(uuid.uuid4()),
            "events": [{"name": event_name, "params": params}],
        }

        url = (
            f"{self._MEASUREMENT_URL}"
            f"?measurement_id={self._measurement_id}"
            f"&api_secret={self._api_secret}"
        )

        try:
            data = json.dumps(payload).encode("utf-8")
            req = request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with request.urlopen(req, timeout=5) as response:
                logger.debug(
                    "GA event '{}' sent, status={}",
                    event_name,
                    response.status,
                )
        except error.URLError as exc:
            logger.warning(
                "Failed to send GA event '{}': {}",
                event_name,
                exc,
            )
