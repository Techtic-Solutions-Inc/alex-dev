import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.config.settings import settings

logger = logging.getLogger(__name__)


def send_confirmation_email(to_email: str) -> None:
    """Send a registration confirmation email via SendGrid."""
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject="Confirm your account",
        html_content=(
            "<p>Thank you for registering with the AI Assistant.</p>"
            f"<p>Please confirm your email address: <strong>{to_email}</strong></p>"
        ),
    )

    client = SendGridAPIClient(settings.SENDGRID_API_KEY)
    response = client.send(message)
    logger.info(
        "Confirmation email sent to %s, status=%s",
        to_email,
        response.status_code,
    )
