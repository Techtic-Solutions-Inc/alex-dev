from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from api.validators.auth import (
    validate_email_not_registered,
    validate_password,
    validate_registration_input,
)
from api.validators.profile import validate_profile_update
from models.schema import ProfileUpdateRequest


class TestValidatePassword:
    def test_accepts_strong_password(self) -> None:
        validate_password("StrongPass1!")

    def test_rejects_weak_password_with_400(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            validate_password("weak")

        assert exc_info.value.status_code == 400
        assert "Password must contain" in exc_info.value.detail

    def test_rejects_no_uppercase(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            validate_password("nouppercase1!")

        assert exc_info.value.status_code == 400
        assert "uppercase" in exc_info.value.detail

    def test_rejects_no_special(self) -> None:
        with pytest.raises(HTTPException) as exc_info:
            validate_password("NoSpecialChar1")

        assert exc_info.value.status_code == 400
        assert "special" in exc_info.value.detail


class TestValidateEmailNotRegistered:
    @pytest.mark.asyncio
    async def test_passes_for_new_email(self) -> None:
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result

        await validate_email_not_registered("new@example.com", db)

    @pytest.mark.asyncio
    async def test_raises_409_for_existing_email(self) -> None:
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = MagicMock()
        db.execute.return_value = result

        with pytest.raises(HTTPException) as exc_info:
            await validate_email_not_registered("taken@example.com", db)

        assert exc_info.value.status_code == 409
        assert "already registered" in exc_info.value.detail


class TestValidateRegistrationInput:
    @pytest.mark.asyncio
    async def test_raises_on_weak_password_before_db_check(self) -> None:
        db = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await validate_registration_input("a@b.com", "short", db)

        assert exc_info.value.status_code == 400
        db.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_raises_on_duplicate_email(self) -> None:
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = MagicMock()
        db.execute.return_value = result

        with pytest.raises(HTTPException) as exc_info:
            await validate_registration_input("taken@a.com", "StrongPass1!", db)

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_passes_valid_input(self) -> None:
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        db.execute.return_value = result

        await validate_registration_input("new@a.com", "StrongPass1!", db)


class TestValidateProfileUpdate:
    def test_accepts_valid_update(self) -> None:
        body = ProfileUpdateRequest(
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            mobile_number="+1234567890",
        )
        validate_profile_update(body)

    def test_rejects_invalid_email_with_400(self) -> None:
        body = ProfileUpdateRequest(email="not-valid-email")
        with pytest.raises(HTTPException) as exc_info:
            validate_profile_update(body)

        assert exc_info.value.status_code == 400
        assert "email" in exc_info.value.detail.lower()

    def test_rejects_invalid_mobile_number_with_400(self) -> None:
        body = ProfileUpdateRequest(mobile_number="abc123")
        with pytest.raises(HTTPException) as exc_info:
            validate_profile_update(body)

        assert exc_info.value.status_code == 400
        assert "mobile number" in exc_info.value.detail.lower()

    def test_rejects_empty_first_name_with_400(self) -> None:
        body = ProfileUpdateRequest(first_name="   ")
        with pytest.raises(HTTPException) as exc_info:
            validate_profile_update(body)

        assert exc_info.value.status_code == 400
        assert "first name" in exc_info.value.detail.lower()

    def test_rejects_empty_last_name_with_400(self) -> None:
        body = ProfileUpdateRequest(last_name="   ")
        with pytest.raises(HTTPException) as exc_info:
            validate_profile_update(body)

        assert exc_info.value.status_code == 400
        assert "last name" in exc_info.value.detail.lower()
