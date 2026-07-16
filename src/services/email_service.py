from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.config.settings import (
    EMAIL_CONFIRMATION_BASE_URL,
    SENDGRID_API_KEY,
    SENDGRID_FROM_EMAIL,
)
from src.utils.logger import logger


class EmailDeliveryError(Exception):
    pass


def send_confirmation_email(to_email: str, confirmation_token: str) -> None:
    confirmation_url = f"{EMAIL_CONFIRMATION_BASE_URL}?token={confirmation_token}"
    message = Mail(
        from_email=SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject="Confirm your email address",
        html_content=(
            "<p>Thank you for registering.</p>"
            f"<p>Please confirm your email address by clicking "
            f'<a href="{confirmation_url}">this link</a>.</p>'
        ),
    )

    if not SENDGRID_API_KEY:
        logger.warning(
            "SENDGRID_API_KEY is not configured; skipping confirmation email to %s",
            to_email,
        )
        return

    try:
        client = SendGridAPIClient(SENDGRID_API_KEY)
        response = client.send(message)
        if response.status_code >= 400:
            raise EmailDeliveryError("Failed to send confirmation email")
        logger.info("Confirmation email sent to %s", to_email)
    except Exception as exc:
        logger.error("Failed to send confirmation email to %s: %s", to_email, exc)
        raise EmailDeliveryError("Failed to send confirmation email") from exc
