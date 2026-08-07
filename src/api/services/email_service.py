"""SendGrid email delivery service."""

from __future__ import annotations

from typing import Any

from loguru import logger

from src.config.settings import Settings, get_settings

__all__ = ["send_confirmation_email", "send_email_verification_email", "send_password_reset_email"]


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


def send_email_verification_email(
    *,
    recipient_email: str,
    recipient_first_name: str,
    verification_token: str,
    settings: Settings | None = None,
) -> str:
    """Send an email verification message and return the verification link."""
    runtime_settings = settings or get_settings()
    verification_link = _build_confirmation_link(runtime_settings, verification_token)

    if not runtime_settings.sendgrid_api_key:
        logger.info(
            "SENDGRID_API_KEY not configured; skipping email delivery to {}",
            recipient_email,
        )
        logger.debug("Verification link: {}", verification_link)
        return verification_link

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=runtime_settings.sendgrid_from_email,
            to_emails=recipient_email,
            subject="Verify your email address",
            html_content=(
                f"<p>Hi {recipient_first_name},</p>"
                "<p>Thanks for registering on the Agentwise portal. To activate your "
                "account and get started, please verify your email address by clicking "
                "the button below.</p>"
                f'<p><a href="{verification_link}">Verify your email address</a></p>'
                "<p>This verification link will expire in 24 hours. If you didn't "
                "create an account on Agentwise, you can safely ignore this email.</p>"
            ),
        )

        dynamic_template_data: dict[str, Any] = {
            "verification_link": verification_link,
            "confirmation_link": verification_link,
            "email": recipient_email,
            "first_name": recipient_first_name,
        }
        template_id = (
            runtime_settings.sendgrid_email_verification_template_id
            or runtime_settings.sendgrid_confirmation_template_id
        )
        if template_id:
            message.template_id = template_id
            message.dynamic_template_data = dynamic_template_data

        client = SendGridAPIClient(runtime_settings.sendgrid_api_key)
        response = client.send(message)
        logger.info(
            "Verification email sent to {} with status {}",
            recipient_email,
            response.status_code,
        )
    except Exception:
        logger.exception(
            "Failed to send verification email to {}; request still succeeded",
            recipient_email,
        )

    return verification_link


def _build_password_reset_link(settings: Settings, token: str) -> str:
    base_url = settings.app_base_url.rstrip("/")
    return f"{base_url}/api/password-recovery/validate/{token}"


def send_password_reset_email(
    *,
    recipient_email: str,
    recipient_first_name: str,
    reset_token: str,
    settings: Settings | None = None,
) -> str:
    """Send a password reset message and return the reset link.

    Password recovery must not fail when transactional email delivery is unavailable.
    The reset link is always returned so non-production clients can surface it.
    """
    runtime_settings = settings or get_settings()
    reset_link = _build_password_reset_link(runtime_settings, reset_token)

    if not runtime_settings.sendgrid_api_key:
        logger.info(
            "SENDGRID_API_KEY not configured; skipping email delivery to {}",
            recipient_email,
        )
        logger.debug("Password reset link: {}", reset_link)
        return reset_link

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=runtime_settings.sendgrid_from_email,
            to_emails=recipient_email,
            subject="Reset your password",
            html_content=(
                f"<p>Hi {recipient_first_name},</p>"
                "<p>We received a request to reset your password.</p>"
                f'<p><a href="{reset_link}">Reset your password</a></p>'
                "<p>This link expires in 30 minutes. If you did not request a "
                "password reset, you can safely ignore this email.</p>"
            ),
        )

        dynamic_template_data: dict[str, Any] = {
            "reset_link": reset_link,
            "email": recipient_email,
            "first_name": recipient_first_name,
        }
        if runtime_settings.sendgrid_password_reset_template_id:
            message.template_id = runtime_settings.sendgrid_password_reset_template_id
            message.dynamic_template_data = dynamic_template_data

        client = SendGridAPIClient(runtime_settings.sendgrid_api_key)
        response = client.send(message)
        logger.info(
            "Password reset email sent to {} with status {}",
            recipient_email,
            response.status_code,
        )
    except Exception:
        logger.exception(
            "Failed to send password reset email to {}; request still succeeded",
            recipient_email,
        )

    return reset_link
