import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending transactional emails via SendGrid."""

    def __init__(
        self,
        api_key: str | None = None,
        from_email: str | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.SENDGRID_API_KEY
        self.from_email = from_email if from_email is not None else settings.SENDGRID_FROM_EMAIL

    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        """Send a password reset email containing the reset link."""
        if not self.api_key or not self.from_email:
            logger.error('SendGrid is not configured; unable to send password reset email')
            raise RuntimeError('Email service is not configured')

        plain_text_content = (
            'You requested a password reset.\n\n'
            f'Click here to reset your password: {reset_link}\n\n'
            'If you did not request this, you can safely ignore this email.'
        )
        html_content = (
            '<p>You requested a password reset.</p>'
            f'<p><a href="{reset_link}">Click here to reset your password.</a></p>'
            '<p>If you did not request this, you can safely ignore this email.</p>'
        )

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject='Password Reset Request',
            plain_text_content=plain_text_content,
            html_content=html_content,
        )

        try:
            client = SendGridAPIClient(self.api_key)
            response = client.send(message)
            logger.info(
                'Password reset email sent to %s (status=%s)',
                to_email,
                response.status_code,
            )
        except Exception as exc:
            logger.error('Failed to send password reset email to %s: %s', to_email, exc)
            raise RuntimeError('Failed to send password reset email') from exc
