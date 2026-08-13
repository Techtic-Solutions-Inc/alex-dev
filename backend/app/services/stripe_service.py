import uuid
from typing import Any

from loguru import logger

from app.core.config import settings


class StripeService:
    """Stripe SDK wrapper for content-related payment features."""

    def __init__(self) -> None:
        self._api_key = settings.STRIPE_SECRET_KEY
        self._enabled = settings.STRIPE_ENABLED

    @property
    def is_configured(self) -> bool:
        return bool(self._enabled and self._api_key)

    def record_content_activity(
        self,
        *,
        event_name: str,
        content_id: uuid.UUID | None = None,
        caption: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Record a content-management activity for payment correlation.

        No-op when Stripe is disabled. When enabled, initializes the Stripe
        SDK (if installed) and logs the activity so payment-related content
        features can correlate later. Never raises — content operations must
        not fail due to Stripe outages.
        """
        if not self.is_configured:
            logger.debug(
                "Stripe not configured; skipping content activity {}",
                event_name,
            )
            return

        payload: dict[str, Any] = {
            "event_name": event_name,
            "content_id": str(content_id) if content_id else None,
            "caption": caption,
            "user_id": user_id,
            "metadata": metadata or {},
        }

        try:
            import stripe  # type: ignore[import-untyped]

            stripe.api_key = self._api_key
            logger.debug(
                "Stripe SDK ready; content activity '{}' recorded: {}",
                event_name,
                payload,
            )
        except ImportError:
            logger.info(
                "Stripe SDK not installed; content activity '{}' logged locally: {}",
                event_name,
                payload,
            )
        except Exception as exc:  # noqa: BLE001 — never fail content ops on Stripe
            logger.warning(
                "Failed to record Stripe content activity '{}': {}",
                event_name,
                exc,
            )
