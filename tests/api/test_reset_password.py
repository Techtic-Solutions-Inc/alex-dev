
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_password_reset_happy_path(client, db_session, test_user):
    # Simulate a valid password reset link
    reset_token = "valid-reset-token"
    new_password = "NewPassword123!"
    response = await client.post(
        "/reset-password",
        json={
            "token": reset_token,
            "new_password": new_password,
            "confirm_password": new_password
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Your password has been reset successfully! You can now log in."


@pytest.mark.asyncio
async def test_password_reset_empty_password(client, db_session, test_user):
    reset_token = "valid-reset-token"
    response = await client.post(
        "/reset-password",
        json={
            "token": reset_token,
            "new_password": "",
            "confirm_password": ""
        }
    )
    assert response.status_code == 400
    assert "Password cannot be empty" in response.json()["detail"]


@pytest.mark.asyncio
async def test_password_reset_mismatched_passwords(client, db_session, test_user):
    reset_token = "valid-reset-token"
    response = await client.post(
        "/reset-password",
        json={
            "token": reset_token,
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!"
        }
    )
    assert response.status_code == 400
    assert "Passwords do not match" in response.json()["detail"]


@pytest.mark.asyncio
async def test_password_reset_invalid_token(client, db_session, test_user):
    reset_token = "invalid-reset-token"
    new_password = "NewPassword123!"
    response = await client.post(
        "/reset-password",
        json={
            "token": reset_token,
            "new_password": new_password,
            "confirm_password": new_password
        }
    )
    assert response.status_code == 400
    assert "Invalid or expired reset token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_password_reset_missing_token(client, db_session, test_user):
    new_password = "NewPassword123!"
    response = await client.post(
        "/reset-password",
        json={
            "new_password": new_password,
            "confirm_password": new_password
        }
    )
    assert response.status_code == 401
    assert "Missing reset token" in response.json()["detail"]
