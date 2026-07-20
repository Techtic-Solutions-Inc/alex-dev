import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta, timezone

from src.main import app
from src.services.auth import hash_password
from src.models.user import User


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def user_with_valid_reset_token(db_session):
    user = User(
        email="user@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token="valid-reset-token-xyz789",
        password_reset_token_expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def user_with_expired_reset_token(db_session):
    user = User(
        email="expired@example.com",
        hashed_password=hash_password("OldPassword123"),
        password_reset_token="expired-reset-token-abc123",
        password_reset_token_expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_password_reset_success(client, user_with_valid_reset_token):
    response = client.post(
        "/reset-password",
        json={
            "token": "valid-reset-token-xyz789",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Your password has been reset successfully! You can now log in."


def test_password_reset_invalid_token(client):
    response = client.post(
        "/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired password reset token."


def test_password_reset_expired_token(client, user_with_expired_reset_token):
    response = client.post(
        "/reset-password",
        json={
            "token": "expired-reset-token-abc123",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired password reset token."


def test_password_reset_mismatched_passwords(client, user_with_valid_reset_token):
    response = client.post(
        "/reset-password",
        json={
            "token": "valid-reset-token-xyz789",
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match."


def test_password_reset_missing_token(client):
    response = client.post(
        "/reset-password",
        json={
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
    )
    assert response.status_code == 422
    assert "token" in response.json()["detail"][0]["loc"]