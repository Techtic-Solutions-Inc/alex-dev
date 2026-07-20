import logging

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.models.user import User
from src.utils.security import hash_password


def test_login_success(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/login",
        json={"email": "user@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["redirect_url"] == "/dashboard"

    payload = jwt.decode(
        data["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert payload["sub"] == str(test_user.id)
    assert payload["email"] == test_user.email


def test_login_invalid_credentials(client: TestClient, test_user: User) -> None:
    wrong_password = client.post(
        "/login",
        json={"email": "user@example.com", "password": "wrong-password"},
    )
    assert wrong_password.status_code == 401
    assert wrong_password.json()["detail"] == "Invalid email or password"

    unknown_email = client.post(
        "/login",
        json={"email": "unknown@example.com", "password": "password123"},
    )
    assert unknown_email.status_code == 401
    assert unknown_email.json()["detail"] == "Invalid email or password"


def test_login_inactive_account(client: TestClient, db_session: Session) -> None:
    user = User(
        email="inactive@example.com",
        hashed_password=hash_password("password123"),
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/login",
        json={"email": "inactive@example.com", "password": "password123"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is inactive"


def test_login_logging(
    client: TestClient,
    test_user: User,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="src.api.v1.controllers.auth_controller"):
        response = client.post(
            "/login",
            json={"email": "user@example.com", "password": "password123"},
        )

    assert response.status_code == 200
    assert any("Login attempt for email=user@example.com" in record.message for record in caplog.records)
    assert any("Login successful for email=user@example.com" in record.message for record in caplog.records)

    caplog.clear()

    with caplog.at_level(logging.WARNING, logger="src.api.v1.controllers.auth_controller"):
        response = client.post(
            "/login",
            json={"email": "user@example.com", "password": "wrong-password"},
        )

    assert response.status_code == 401
    assert any(
        "Login failed: invalid credentials for email=user@example.com" in record.message
        for record in caplog.records
    )
