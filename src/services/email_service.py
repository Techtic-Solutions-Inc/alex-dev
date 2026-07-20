"""SendGrid email integration."""

import logging
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails via SendGrid."""

    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.SENDGRID_API_KEY
        self.from_email = from_email if from_email is not None else settings.SENDGRID_FROM_EMAIL
        self.app_name = settings.APP_NAME

    def send_confirmation_email(self, to_email: str) -> None:
        """Send account confirmation email to a newly registered user."""
        subject = f"Confirm your {self.app_name} account"
        html_content = (
            f"<p>Welcome to {self.app_name}!</p>"
            f"<p>Your account has been created successfully. "
            f"Please confirm your email address to activate your account.</p>"
        )

        if not self.api_key:
            logger.warning(
                "SENDGRID_API_KEY is not configured; skipping confirmation email to %s",
                to_email,
            )
            return

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )

        try:
            client = SendGridAPIClient(self.api_key)
            response = client.send(message)
            logger.info(
                "Confirmation email sent to %s (status=%s)",
                to_email,
                response.status_code,
            )
        except Exception:
            logger.exception("Failed to send confirmation email to %s", to_email)
            raise
