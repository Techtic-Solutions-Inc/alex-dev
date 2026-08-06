import pytest
from httpx import AsyncClient
from unittest.mock import patch

from src.api.models.user import User
from src.utils.password import hash_password

@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, db_session):
    response = await client.post(
        "/api/auth/signup",
        json={"email": "newuser@example.com", "password": "StrongPassword123!"}
    )
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert "id" in response.json()["data"]

@pytest.mark.asyncio
async def test_signup_invalid_email_format(client: AsyncClient):
    response = await client.post(
        "/api/auth/signup",
        json={"email": "invalid-email", "password": "StrongPassword123!"}
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, db_session):
    existing_user = User(
        username="existinguser",
        email="existing@example.com",
        password_hash=hash_password("ExistingPassword123!")
    )
    db_session.add(existing_user)
    db_session.commit()

    response = await client.post(
        "/api/auth/signup",
        json={"email": "existing@example.com", "password": "StrongPassword123!"}
    )
    assert response.status_code == 409
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"

@pytest.mark.asyncio
@patch("src.api.services.email_service.send_confirmation_email")
async def test_signup_confirmation_email(mock_send_email, client: AsyncClient):
    mock_send_email.return_value = None
    response = await client.post(
        "/api/auth/signup",
        json={"email": "newuser@example.com", "password": "StrongPassword123!"}
    )
    assert response.status_code == 201
    mock_send_email.assert_called_once()

@pytest.mark.asyncio
async def test_signup_password_strength(client: AsyncClient):
    response = await client.post(
        "/api/auth/signup",
        json={"email": "user@example.com", "password": "weak"}
    )
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
