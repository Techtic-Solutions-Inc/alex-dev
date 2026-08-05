from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from api.services.registration_service import create_registered_user
from models.schema import RegisterRequest, RegisterResponse


def _mock_db_session(existing_user=None) -> AsyncMock:
    """Create a mock async database session."""
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing_user
    session.execute.return_value = result
    return session


class TestCreateRegisteredUser:
    @pytest.mark.asyncio
    async def test_sends_confirmation_email(self) -> None:
        db = _mock_db_session(existing_user=None)
        body = RegisterRequest(email="new@example.com", password="StrongPass1!")

        with (
            patch(
                "api.services.registration_service.register_user",
                new_callable=AsyncMock,
                return_value=RegisterResponse(
                    email="new@example.com",
                    message="Registration successful. Please check your email to confirm your account.",
                ),
            ),
            patch(
                "api.services.registration_service.validate_registration_input",
                new_callable=AsyncMock,
            ),
            patch(
                "api.services.registration_service.send_confirmation_email_async",
                new_callable=AsyncMock,
            ) as mock_send_email,
            patch(
                "api.services.registration_service.generate_confirmation_token",
                return_value="test-token",
            ),
        ):
            response = await create_registered_user(body, db)

        assert response.email == "new@example.com"
        assert "Registration successful" in response.message
        mock_send_email.assert_called_once_with("new@example.com", "test-token")

    @pytest.mark.asyncio
    async def test_email_failure_raises_503(self) -> None:
        db = _mock_db_session(existing_user=None)
        body = RegisterRequest(email="fail@example.com", password="StrongPass1!")

        with (
            patch(
                "api.services.registration_service.register_user",
                new_callable=AsyncMock,
                return_value=RegisterResponse(
                    email="fail@example.com",
                    message="Registration successful. Please check your email to confirm your account.",
                ),
            ),
            patch(
                "api.services.registration_service.validate_registration_input",
                new_callable=AsyncMock,
            ),
            patch(
                "api.services.registration_service.send_confirmation_email_async",
                new_callable=AsyncMock,
                side_effect=RuntimeError("SendGrid down"),
            ),
            patch(
                "api.services.registration_service.generate_confirmation_token",
                return_value="test-token",
            ),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await create_registered_user(body, db)

        assert exc_info.value.status_code == 503
        assert "confirmation email" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_weak_password_raises_400(self) -> None:
        db = _mock_db_session()
        body = RegisterRequest(email="x@example.com", password="weakpass!")

        with pytest.raises(HTTPException) as exc_info:
            await create_registered_user(body, db)

        assert exc_info.value.status_code == 400
        assert "Password must contain" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_duplicate_email_raises_409(self) -> None:
        existing = MagicMock()
        db = _mock_db_session(existing_user=existing)
        body = RegisterRequest(email="dup@example.com", password="StrongPass1!")

        with pytest.raises(HTTPException) as exc_info:
            await create_registered_user(body, db)

        assert exc_info.value.status_code == 409
        assert "already registered" in exc_info.value.detail
