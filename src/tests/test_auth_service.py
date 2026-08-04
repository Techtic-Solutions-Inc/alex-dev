from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from models.schema import LoginRequest, RegisterRequest
from services.auth import confirm_email, login_user, register_user


def _mock_db_session(existing_user=None) -> AsyncMock:
    """Create a mock async database session."""
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing_user
    session.execute.return_value = result
    return session


class TestRegisterUser:
    @pytest.mark.asyncio
    async def test_successful_registration(self) -> None:
        db = _mock_db_session(existing_user=None)

        body = RegisterRequest(email="new@example.com", password="StrongPass1!")
        response = await register_user(body, db)

        assert response.email == "new@example.com"
        assert "Registration successful" in response.message
        db.add.assert_called_once()
        db.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_weak_password_raises_400(self) -> None:
        db = _mock_db_session()
        body = RegisterRequest(email="x@example.com", password="weakpass!")

        with pytest.raises(HTTPException) as exc_info:
            await register_user(body, db)

        assert exc_info.value.status_code == 400
        assert "Password must contain" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_duplicate_email_raises_409(self) -> None:
        existing = MagicMock()
        db = _mock_db_session(existing_user=existing)
        body = RegisterRequest(email="dup@example.com", password="StrongPass1!")

        with pytest.raises(HTTPException) as exc_info:
            await register_user(body, db)

        assert exc_info.value.status_code == 409
        assert "already registered" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_integrity_error_raises_409(self) -> None:
        db = _mock_db_session(existing_user=None)
        db.flush.side_effect = IntegrityError("dup", {}, Exception())

        body = RegisterRequest(email="race@example.com", password="StrongPass1!")

        with pytest.raises(HTTPException) as exc_info:
            await register_user(body, db)

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_email_lowercased(self) -> None:
        db = _mock_db_session(existing_user=None)

        body = RegisterRequest(email="MiXeD@Example.COM", password="StrongPass1!")
        response = await register_user(body, db)

        assert response.email == "mixed@example.com"


class TestLoginUser:
    @pytest.mark.asyncio
    async def test_invalid_credentials_raises_401(self) -> None:
        db = _mock_db_session(existing_user=None)
        body = LoginRequest(email="nope@example.com", password="any")

        with pytest.raises(HTTPException) as exc_info:
            await login_user(body, db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_password_raises_401(self) -> None:
        user = MagicMock()
        user.hashed_password = "not_a_real_hash"
        db = _mock_db_session(existing_user=user)

        with patch("services.auth.verify_password", return_value=False):
            body = LoginRequest(email="user@example.com", password="wrong")
            with pytest.raises(HTTPException) as exc_info:
                await login_user(body, db)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_successful_login_returns_token(self) -> None:
        user = MagicMock()
        user.id = 1
        user.email = "user@example.com"
        user.hashed_password = "hashed"
        db = _mock_db_session(existing_user=user)

        with patch("services.auth.verify_password", return_value=True):
            body = LoginRequest(email="user@example.com", password="any")
            response = await login_user(body, db)

        assert response.session_token


class TestConfirmEmail:
    @pytest.mark.asyncio
    async def test_invalid_token_raises_400(self) -> None:
        db = _mock_db_session()

        with pytest.raises(HTTPException) as exc_info:
            await confirm_email("bad-token", db)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_user_not_found_raises_404(self) -> None:
        db = _mock_db_session(existing_user=None)

        with patch(
            "services.auth.decode_confirmation_token",
            return_value="missing@example.com",
        ), pytest.raises(HTTPException) as exc_info:
            await confirm_email("valid-token", db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_already_confirmed_returns_message(self) -> None:
        user = MagicMock()
        user.is_confirmed = True
        user.email = "confirmed@example.com"
        db = _mock_db_session(existing_user=user)

        with patch(
            "services.auth.decode_confirmation_token",
            return_value="confirmed@example.com",
        ):
            response = await confirm_email("valid-token", db)

        assert "already confirmed" in response.message

    @pytest.mark.asyncio
    async def test_successful_confirmation(self) -> None:
        user = MagicMock()
        user.is_confirmed = False
        user.email = "user@example.com"
        db = _mock_db_session(existing_user=user)

        with patch(
            "services.auth.decode_confirmation_token",
            return_value="user@example.com",
        ):
            response = await confirm_email("valid-token", db)

        assert user.is_confirmed is True
        assert "confirmed successfully" in response.message
