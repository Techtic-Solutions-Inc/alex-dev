from unittest.mock import MagicMock

from fastapi import status

from src.services.auth0_service import AuthenticationError
from tests.conftest import build_auth0_token_response


def test_authenticate_success(client, mock_auth0_service: MagicMock) -> None:
    mock_auth0_service.authenticate.return_value = build_auth0_token_response()

    response = client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@example.com", "password": "valid-password"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "test-access-token"
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 86400
    assert data["redirect_url"] == "/dashboard"
    assert data["user"]["email"] == "user@example.com"
    assert data["user"]["id"]

    mock_auth0_service.authenticate.assert_called_once_with("user@example.com", "valid-password")


def test_authenticate_invalid_credentials(client, mock_auth0_service: MagicMock) -> None:
    mock_auth0_service.authenticate.side_effect = AuthenticationError("Invalid email or password")

    response = client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@example.com", "password": "wrong-password"},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid email or password"}


def test_authenticate_missing_fields(client) -> None:
    response = client.post("/api/v1/user/authenticate", json={"email": "user@example.com"})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()
