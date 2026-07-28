from unittest.mock import patch

from fastapi import status

from src.services.auth_service import AuthenticationError


@patch("src.api.v1.authenticate.authenticate_with_auth0")
def test_authenticate_success(mock_authenticate, client):
    mock_authenticate.return_value = {
        "access_token": "test-access-token",
        "token_type": "Bearer",
    }

    response = client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@example.com", "password": "securepassword"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "test-access-token"
    assert data["token_type"] == "Bearer"
    assert data["redirect_url"] == "/dashboard"
    mock_authenticate.assert_called_once_with("user@example.com", "securepassword")


@patch("src.api.v1.authenticate.authenticate_with_auth0")
def test_authenticate_invalid_credentials(mock_authenticate, client):
    mock_authenticate.side_effect = AuthenticationError("Invalid credentials")

    response = client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid credentials"}


def test_authenticate_missing_fields(client):
    response = client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@example.com"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
