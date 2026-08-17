"""Transactional email delivery through SendGrid."""

from __future__ import annotations

import logging
from urllib.parse import urlencode, urlsplit, urlunsplit

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Send account emails without exposing provider failures to API clients."""

    def send_verification_email(self, recipient: str, token: str) -> None:
        """Send the configured verification email when SendGrid is available."""
        if not settings.SENDGRID_API_KEY or not settings.SENDGRID_FROM_EMAIL:
            logger.warning(
                "Verification email was not sent because SendGrid is not configured."
            )
            return

        verification_url = self._verification_url(token)
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=recipient,
                subject="Verify your email address",
                html_content=(
                    "<p>Welcome. Confirm your email address to complete your account "
                    f'<a href="{verification_url}">verification</a>.</p>'
                ),
            )
            response = SendGridAPIClient(settings.SENDGRID_API_KEY).send(message)
            if not 200 <= response.status_code < 300:
                logger.error(
                    "SendGrid rejected verification email with status %s.",
                    response.status_code,
                )
        except Exception:
            logger.exception("Unable to send verification email.")

    @staticmethod
    def _verification_url(token: str) -> str:
        """Append the signed verification token without losing existing query data."""
        parts = urlsplit(settings.EMAIL_VERIFICATION_URL)
        query = parts.query
        token_query = urlencode({"token": token})
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, "&".join(filter(None, (query, token_query))), parts.fragment)
        )
