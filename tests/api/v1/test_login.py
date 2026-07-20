"""Tests for login endpoint."""

from fastapi.testclient import TestClient

VALID_PASSWORD = "StrongPass1!"


def test_login_success(client: TestClient, mock_sendgrid) -> None:
    """Valid credentials return an access token."""
    email = "loginuser@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": VALID_PASSWORD},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": VALID_PASSWORD},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["email"] == email


def test_login_invalid_credentials(client: TestClient) -> None:
    """Invalid credentials are rejected."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "WrongPass1!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."
