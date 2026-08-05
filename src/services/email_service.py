import asyncio
import os

from loguru import logger
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from config.settings import APP_BASE_URL, SENDGRID_API_KEY, SENDGRID_FROM_EMAIL


def _get_sendgrid_config() -> tuple[str, str]:
    """Resolve SendGrid API key and sender email, raising on missing values."""
    api_key = SENDGRID_API_KEY or os.getenv("SENDGRID_API_KEY")
    from_email = SENDGRID_FROM_EMAIL or os.getenv("SENDGRID_FROM_EMAIL")

    if not api_key:
        raise RuntimeError("SENDGRID_API_KEY environment variable is not set")
    if not from_email:
        raise RuntimeError("SENDGRID_FROM_EMAIL environment variable is not set")

    return api_key, from_email


def _build_confirmation_message(to_email: str, confirmation_token: str) -> Mail:
    """Build the confirmation email message."""
    _, from_email = _get_sendgrid_config()
    confirmation_url = (
        f"{APP_BASE_URL.rstrip('/')}/auth/confirm?token={confirmation_token}"
    )
    return Mail(
        from_email=from_email,
        to_emails=to_email,
        subject="Confirm your email address",
        html_content=(
            "<p>Thank you for registering.</p>"
            f"<p>Please confirm your email by clicking "
            f'<a href="{confirmation_url}">this link</a>.</p>'
        ),
    )


def send_confirmation_email(to_email: str, confirmation_token: str) -> None:
    """Send a registration confirmation email via SendGrid (synchronous)."""
    api_key, _ = _get_sendgrid_config()
    message = _build_confirmation_message(to_email, confirmation_token)

    client = SendGridAPIClient(api_key)
    response = client.send(message)

    status_code = getattr(response, "status_code", 202)
    if status_code >= 400:
        logger.error(
            "SendGrid confirmation email failed for {} with status {}",
            to_email,
            status_code,
        )
        raise RuntimeError("Failed to send confirmation email")


async def send_confirmation_email_async(to_email: str, confirmation_token: str) -> None:
    """Send a registration confirmation email via SendGrid (async-safe wrapper)."""
    await asyncio.to_thread(send_confirmation_email, to_email, confirmation_token)
