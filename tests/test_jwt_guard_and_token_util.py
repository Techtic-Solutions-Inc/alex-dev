"""Tests for JWT guard and token utilities."""

from fastapi.testclient import TestClient

from app.common.utils.token import generate_token
from app.core.security import create_access_token, decode_token


def test_generate_token_returns_signed_access_token() -> None:
    token = generate_token("user-123")
    payload = decode_token(token, "access")
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_login_and_access_protected_route(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "johndoe", "password": "secret"},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["success"] is True
    assert login_body["message"] == "Login successful."
    assert login_body["data"]["token_type"] == "bearer"
    assert isinstance(login_body["data"]["access_token"], str)

    token = login_body["data"]["access_token"]
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json() == {
        "success": True,
        "message": "Authenticated.",
        "data": {"subject": "johndoe"},
    }


def test_protected_route_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "message": "Authentication is required.",
        "error": {"code": "AUTHENTICATION_REQUIRED", "details": None},
    }


def test_protected_route_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-token"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "message": "The access token is invalid or expired.",
        "error": {"code": "INVALID_ACCESS_TOKEN", "details": None},
    }


def test_login_rejects_invalid_credentials(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "johndoe", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "success": False,
        "message": "Invalid credentials.",
        "error": {"code": "INVALID_CREDENTIALS", "details": None},
    }


def test_refresh_token_cannot_access_protected_route(client: TestClient) -> None:
    from app.core.security import create_refresh_token

    refresh_token = create_refresh_token("johndoe")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_ACCESS_TOKEN"
