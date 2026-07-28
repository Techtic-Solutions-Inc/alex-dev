from unittest.mock import AsyncMock, patch

import pytest

from src.models.user import User


@pytest.fixture
def auth0_token_response():
    return {
        "access_token": "test-access-token",
        "token_type": "Bearer",
        "expires_in": 86400,
    }


def test_authenticate_success(client, db_session, auth0_token_response):
    user = User(email="user@example.com", password_hash=User.hash_password("correct-password"))
    db_session.add(user)
    db_session.commit()

    with patch(
        "src.api.v1.authenticate.Auth0Service.authenticate",
        new=AsyncMock(return_value=auth0_token_response),
    ):
        response = client.post(
            "/api/v1/user/authenticate",
            json={"email": "user@example.com", "password": "correct-password"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "test-access-token"
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 86400
    assert data["redirect_url"] == "/dashboard"
    assert data["email"] == "user@example.com"


def test_authenticate_invalid_credentials(client, db_session):
    user = User(email="user@example.com", password_hash=User.hash_password("correct-password"))
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error"] == "invalid_credentials"
    assert data["detail"]["message"] == "Invalid email or password"


def test_authenticate_missing_fields(client):
    response = client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@example.com"},
    )

    assert response.status_code == 422

    response = client.post(
        "/api/v1/user/authenticate",
        json={"password": "secret"},
    )

    assert response.status_code == 422
