
import pytest
from httpx import AsyncClient
from unittest.mock import patch

from src.api.models.user import User


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient, db_session):
    # Act
    with patch('src.api.services.user_service.send_confirmation_email', return_value=True):
        response = await client.post(
            "/api/auth/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "password": "SecurePassword123!",
                "terms_accepted": True
            }
        )

    # Assert
    assert response.status_code == 201
    assert response.json()["data"]["email"] == "john.doe@example.com"


@pytest.mark.asyncio
async def test_signup_missing_first_name(client: AsyncClient):
    # Act
    response = await client.post(
        "/api/auth/signup",
        json={
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePassword123!",
            "terms_accepted": True
        }
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["message"] == "First name is required."


@pytest.mark.asyncio
async def test_signup_invalid_email_format(client: AsyncClient):
    # Act
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "terms_accepted": True
        }
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["message"] == "Invalid email format."


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, db_session):
    # Arrange
    user = User(
        email="john.doe@example.com",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Act
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePassword123!",
            "terms_accepted": True
        }
    )

    # Assert
    assert response.status_code == 409
    assert response.json()["message"] == "Email already exists."


@pytest.mark.asyncio
async def test_signup_terms_not_accepted(client: AsyncClient):
    # Act
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "SecurePassword123!",
            "terms_accepted": False
        }
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["message"] == "Terms must be accepted."
