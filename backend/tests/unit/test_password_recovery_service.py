from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from app.core.config import settings
from app.core.security import (
    create_password_reset_token,
    verify_password_reset_token,
)
from app.exceptions.http_exceptions import NotFoundException
from app.schemas.password_recovery import PasswordRecoveryRequest
from app.services.email_service import EmailService
from app.services.password_recovery_service import PasswordRecoveryService


def test_create_and_verify_password_reset_token() -> None:
    token = create_password_reset_token(
        user_id="user-123",
        email="user@example.com",
        expires_delta=timedelta(minutes=30),
    )
    payload = verify_password_reset_token(token)
    assert payload["sub"] == "user-123"
    assert payload["email"] == "user@example.com"
    assert payload["type"] == "password_reset"


def test_password_reset_token_expires_after_30_minutes() -> None:
    token = create_password_reset_token(
        user_id="user-123",
        email="user@example.com",
        expires_delta=timedelta(minutes=-1),
    )
    with pytest.raises(ValueError, match="Invalid or expired password reset token"):
        verify_password_reset_token(token)


def test_password_reset_token_rejects_access_token() -> None:
    from app.core.security import create_access_token

    token = create_access_token({"sub": "user-123"})
    with pytest.raises(ValueError, match="Invalid or expired password reset token"):
        verify_password_reset_token(token)


def test_email_service_skips_send_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "")
    monkeypatch.setattr(settings, "SENDGRID_FROM_EMAIL", "noreply@example.com")

    service = EmailService()
    assert service.is_configured is False

    with patch("urllib.request.urlopen") as mock_urlopen:
        service.send_password_reset_email(
            to_email="user@example.com",
            reset_link="http://localhost:3000/reset-password?token=abc",
            expires_minutes=30,
        )
        mock_urlopen.assert_not_called()


def test_email_service_sends_via_sendgrid_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "SENDGRID_API_KEY", "sg-test-key")
    monkeypatch.setattr(settings, "SENDGRID_FROM_EMAIL", "noreply@example.com")
    monkeypatch.setattr(settings, "SENDGRID_FROM_NAME", "Support")

    service = EmailService()
    assert service.is_configured is True

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.status = 202
        service.send_password_reset_email(
            to_email="user@example.com",
            reset_link="http://localhost:3000/reset-password?token=abc",
            expires_minutes=30,
        )
        mock_urlopen.assert_called_once()


def test_password_recovery_service_user_not_found() -> None:
    db = MagicMock()
    repo = MagicMock()
    repo.get_by_email.return_value = None
    email_service = MagicMock()

    service = PasswordRecoveryService(db, email_service=email_service)
    service.user_repository = repo

    with pytest.raises(NotFoundException) as exc_info:
        service.initiate_password_recovery(
            PasswordRecoveryRequest(email="missing@example.com")
        )

    assert exc_info.value.code == "USER_NOT_FOUND"
    email_service.send_password_reset_email.assert_not_called()


def test_password_recovery_service_sends_email() -> None:
    user = MagicMock()
    user.id = "550e8400-e29b-41d4-a716-446655440000"
    user.email = "user@example.com"

    db = MagicMock()
    repo = MagicMock()
    repo.get_by_email.return_value = user
    email_service = MagicMock()

    service = PasswordRecoveryService(db, email_service=email_service)
    service.user_repository = repo

    result = service.initiate_password_recovery(
        PasswordRecoveryRequest(email="user@example.com")
    )

    assert result.email == "user@example.com"
    assert result.expires_in == 1800
    email_service.send_password_reset_email.assert_called_once()
    call_kwargs = email_service.send_password_reset_email.call_args.kwargs
    assert call_kwargs["to_email"] == "user@example.com"
    assert call_kwargs["expires_minutes"] == 30
    assert "token=" in call_kwargs["reset_link"]
