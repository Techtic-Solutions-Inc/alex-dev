
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from src.api.models.user import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session):
    # Arrange
    user = User(
        email="user@example.com",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Act
    with patch('src.api.services.auth0_service.Auth0AuthenticationService.authenticate', return_value=True):
        response = await client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "securePassword123"}
        )

    # Assert
    assert response.status_code == 201
    assert "access_token" in response.json()["data"]


@pytest.mark.asyncio
async def test_login_empty_fields(client: AsyncClient):
    # Act
    response = await client.post(
        "/api/auth/login",
        json={"email": "", "password": ""}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["message"] == "Email and password are required."


@pytest.mark.asyncio
async def test_login_incorrect_password(client: AsyncClient, db_session):
    # Arrange
    user = User(
        email="user@example.com",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Act
    with patch('src.api.services.auth0_service.Auth0AuthenticationService.authenticate', side_effect=Exception("Incorrect password")):
        response = await client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "wrongPassword"}
        )

    # Assert
    assert response.status_code == 409
    assert response.json()["message"] == "Incorrect email or password."


@pytest.mark.asyncio
async def test_protected_route_without_token(client: AsyncClient):
    # Act
    response = await client.get("/api/auth/session")

    # Assert
    assert response.status_code == 403
    assert response.json()["message"] == "Not authenticated"


@pytest.mark.asyncio
async def test_auth0_integration(client: AsyncClient, db_session):
    # Arrange
    user = User(
        email="user@example.com",
        password_hash="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Act
    with patch('src.api.services.auth0_service.Auth0AuthenticationService.authenticate', return_value=True):
        response = await client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "securePassword123"}
        )

    # Assert
    assert response.status_code == 201
    assert "access_token" in response.json()["data"]
