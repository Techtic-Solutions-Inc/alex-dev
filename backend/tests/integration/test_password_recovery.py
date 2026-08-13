import uuid
from unittest.mock import MagicMock

import pytest
from app.core.security import hash_password
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_initiate_password_recovery_valid_email(
    client: AsyncClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = f"recover-ok-{uuid.uuid4()}@example.com"
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
            "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false, 'user')"
        ),
        {
            "id": uuid.uuid4(),
            "username": email,
            "email": email,
            "first_name": "Jane",
            "last_name": "Doe",
            "hashed_password": hash_password("securePassword123"),
        },
    )
    db_session.flush()

    mock_send = MagicMock()
    monkeypatch.setattr(
        "app.services.email_service.EmailService.send_password_reset_email",
        mock_send,
    )

    response = await client.post(
        "/api/auth/password-recovery",
        json={"email": email},
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "success": True,
        "message": "Password recovery email sent successfully",
        "data": {
            "email": email,
            "expires_in": 1800,
        },
    }
    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args.kwargs
    assert call_kwargs["to_email"] == email
    assert "token=" in call_kwargs["reset_link"]
    assert call_kwargs["expires_minutes"] == 30


@pytest.mark.asyncio
async def test_initiate_password_recovery_invalid_email(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/auth/password-recovery",
        json={"email": "invalid-email"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    email_errors = [
        item for item in body["error"]["details"] if item["field"] == "email"
    ]
    assert len(email_errors) == 1


@pytest.mark.asyncio
async def test_initiate_password_recovery_empty_email(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/auth/password-recovery",
        json={"email": ""},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    email_errors = [
        item for item in body["error"]["details"] if item["field"] == "email"
    ]
    assert len(email_errors) == 1


@pytest.mark.asyncio
async def test_initiate_password_recovery_missing_email(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/auth/password-recovery",
        json={},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    email_errors = [
        item for item in body["error"]["details"] if item["field"] == "email"
    ]
    assert len(email_errors) == 1


@pytest.mark.asyncio
async def test_initiate_password_recovery_nonexistent_email(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/auth/password-recovery",
        json={"email": f"missing-{uuid.uuid4()}@example.com"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "No account is associated with this email address"
    assert body["error"] == {
        "code": "USER_NOT_FOUND",
        "details": None,
    }
