import json
from urllib import error, request

from loguru import logger

from app.core.config import settings
from app.exceptions.http_exceptions import BadRequestException


class EmailService:
    """Send transactional emails via the SendGrid Web API."""

    _SEND_URL = "https://api.sendgrid.com/v3/mail/send"

    def __init__(self) -> None:
        self._api_key = settings.SENDGRID_API_KEY
        self._from_email = settings.SENDGRID_FROM_EMAIL
        self._from_name = settings.SENDGRID_FROM_NAME

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._from_email)

    def send_password_reset_email(
        self,
        *,
        to_email: str,
        reset_link: str,
        expires_minutes: int,
    ) -> None:
        """Send a password reset email containing the time-limited reset link."""
        subject = "Reset your password"
        plain_text = (
            "You requested a password reset.\n\n"
            f"Open this link to choose a new password (expires in "
            f"{expires_minutes} minutes):\n{reset_link}\n\n"
            "If you did not request this, you can ignore this email."
        )
        html_content = (
            "<p>You requested a password reset.</p>"
            f"<p><a href=\"{reset_link}\">Reset your password</a> "
            f"(link expires in {expires_minutes} minutes).</p>"
            "<p>If you did not request this, you can ignore this email.</p>"
        )

        if not self.is_configured:
            logger.info(
                "SendGrid not configured; password reset email for {} "
                "would use link {}",
                to_email,
                reset_link,
            )
            return

        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {
                "email": self._from_email,
                "name": self._from_name,
            },
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": plain_text},
                {"type": "text/html", "value": html_content},
            ],
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = request.Request(
                self._SEND_URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with request.urlopen(req, timeout=10) as response:
                logger.debug(
                    "Password reset email sent to {}, status={}",
                    to_email,
                    response.status,
                )
        except error.HTTPError as exc:
            logger.error(
                "SendGrid rejected password reset email for {}: {}",
                to_email,
                exc.code,
            )
            raise BadRequestException(
                message="Unable to send password recovery email. Please try again later.",
                code="EMAIL_SEND_FAILED",
            ) from exc
        except error.URLError as exc:
            logger.error(
                "Failed to reach SendGrid for password reset email to {}: {}",
                to_email,
                exc,
            )
            raise BadRequestException(
                message="Unable to send password recovery email. Please try again later.",
                code="EMAIL_SEND_FAILED",
            ) from exc
