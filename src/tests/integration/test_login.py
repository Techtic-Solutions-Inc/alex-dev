"""Integration tests for login and protected routes."""

from fastapi.testclient import TestClient

from src.api.models.user import User


def test_login_success(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "TestUser123!",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["email"] == "testuser@example.com"
    assert body["data"]["id"] == str(test_user.id)
    assert body["data"]["redirect"] == "/dashboard"
    assert body["data"]["link"] == "/dashboard"
    assert body["data"]["description"]


def test_login_empty_fields(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "email": "",
            "password": "",
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] in {"EMPTY_EMAIL", "EMPTY_PASSWORD", "VALIDATION_ERROR"}
    assert any(error["field"] == "email" for error in body["errors"])
    assert any(error["field"] == "password" for error in body["errors"])


def test_login_incorrect_password(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/api/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INCORRECT_PASSWORD"
    assert body["message"] == "Incorrect email or password."


def test_protected_route_without_token(client: TestClient) -> None:
    response = client.get("/protected-endpoint")
    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"
