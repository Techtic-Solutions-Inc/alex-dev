"""SendGrid email delivery service."""

from __future__ import annotations

from typing import Any

from loguru import logger

from src.config.settings import Settings, get_settings

__all__ = ["send_confirmation_email"]


def _build_confirmation_link(settings: Settings, token: str) -> str:
    base_url = settings.app_base_url.rstrip("/")
    return f"{base_url}/api/auth/confirm-email?token={token}"


def send_confirmation_email(
    *,
    recipient_email: str,
    recipient_first_name: str,
    confirmation_token: str,
    settings: Settings | None = None,
) -> str:
    """Send an email confirmation message and return the confirmation link.

    Registration must not fail when transactional email delivery is unavailable.
    The confirmation link is always returned so non-production clients can surface it.
    """
    runtime_settings = settings or get_settings()
    confirmation_link = _build_confirmation_link(runtime_settings, confirmation_token)

    if not runtime_settings.sendgrid_api_key:
        logger.info(
            "SENDGRID_API_KEY not configured; skipping email delivery to {}",
            recipient_email,
        )
        logger.debug("Confirmation link: {}", confirmation_link)
        return confirmation_link

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=runtime_settings.sendgrid_from_email,
            to_emails=recipient_email,
            subject="Confirm your email address",
            html_content=(
                f"<p>Hi {recipient_first_name},</p>"
                "<p>Thank you for signing up.</p>"
                f'<p><a href="{confirmation_link}">Confirm your email address</a></p>'
            ),
        )

        dynamic_template_data: dict[str, Any] = {
            "confirmation_link": confirmation_link,
            "email": recipient_email,
            "first_name": recipient_first_name,
        }
        if runtime_settings.sendgrid_confirmation_template_id:
            message.template_id = runtime_settings.sendgrid_confirmation_template_id
            message.dynamic_template_data = dynamic_template_data

        client = SendGridAPIClient(runtime_settings.sendgrid_api_key)
        response = client.send(message)
        logger.info(
            "Confirmation email sent to {} with status {}",
            recipient_email,
            response.status_code,
        )
    except Exception:
        logger.exception(
            "Failed to send confirmation email to {}; registration still succeeded",
            recipient_email,
        )

    return confirmation_link
