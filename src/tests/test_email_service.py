from unittest.mock import MagicMock, patch

import pytest

from services.email_service import (
    _build_confirmation_message,
    _get_sendgrid_config,
    send_confirmation_email,
)


class TestGetSendgridConfig:
    @patch.dict(
        "os.environ",
        {"SENDGRID_API_KEY": "test-key", "SENDGRID_FROM_EMAIL": "test@example.com"},
    )
    @patch("services.email_service.SENDGRID_API_KEY", "test-key")
    @patch("services.email_service.SENDGRID_FROM_EMAIL", "test@example.com")
    def test_returns_config_when_set(self) -> None:
        api_key, from_email = _get_sendgrid_config()
        assert api_key == "test-key"
        assert from_email == "test@example.com"

    @patch("services.email_service.SENDGRID_API_KEY", None)
    @patch.dict("os.environ", {}, clear=True)
    def test_raises_when_api_key_missing(self) -> None:
        with pytest.raises(RuntimeError, match="SENDGRID_API_KEY"):
            _get_sendgrid_config()

    @patch("services.email_service.SENDGRID_API_KEY", "test-key")
    @patch("services.email_service.SENDGRID_FROM_EMAIL", None)
    @patch.dict("os.environ", {"SENDGRID_API_KEY": "test-key"}, clear=True)
    def test_raises_when_from_email_missing(self) -> None:
        with pytest.raises(RuntimeError, match="SENDGRID_FROM_EMAIL"):
            _get_sendgrid_config()


class TestBuildConfirmationMessage:
    @patch("services.email_service.SENDGRID_API_KEY", "test-key")
    @patch("services.email_service.SENDGRID_FROM_EMAIL", "sender@example.com")
    @patch("services.email_service.APP_BASE_URL", "https://app.example.com")
    def test_message_contains_confirmation_link(self) -> None:
        msg = _build_confirmation_message("user@example.com", "abc123")
        assert msg.from_email.email == "sender@example.com"

        personalizations = msg.personalizations
        assert len(personalizations) == 1
        to_list = personalizations[0].tos
        assert any(t["email"] == "user@example.com" for t in to_list)

        html_content = msg.contents[0].content
        assert "https://app.example.com/auth/confirm?token=abc123" in html_content

    @patch("services.email_service.SENDGRID_API_KEY", "test-key")
    @patch("services.email_service.SENDGRID_FROM_EMAIL", "sender@example.com")
    @patch("services.email_service.APP_BASE_URL", "https://app.example.com/")
    def test_strips_trailing_slash_from_base_url(self) -> None:
        msg = _build_confirmation_message("user@example.com", "tok")
        html_content = msg.contents[0].content
        assert "https://app.example.com/auth/confirm?token=tok" in html_content
        assert "//auth" not in html_content


class TestSendConfirmationEmail:
    @patch("services.email_service.SENDGRID_API_KEY", "test-key")
    @patch("services.email_service.SENDGRID_FROM_EMAIL", "sender@example.com")
    @patch("services.email_service.SendGridAPIClient")
    def test_calls_sendgrid_client(self, mock_client_cls: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client_cls.return_value.send.return_value = mock_response

        send_confirmation_email("user@example.com", "tok123")

        mock_client_cls.assert_called_once_with("test-key")
        mock_client_cls.return_value.send.assert_called_once()

    @patch("services.email_service.SENDGRID_API_KEY", "test-key")
    @patch("services.email_service.SENDGRID_FROM_EMAIL", "sender@example.com")
    @patch("services.email_service.SendGridAPIClient")
    def test_raises_on_sendgrid_error(self, mock_client_cls: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client_cls.return_value.send.return_value = mock_response

        with pytest.raises(RuntimeError, match="Failed to send"):
            send_confirmation_email("user@example.com", "tok123")
