"""Integration tests for authentication endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.utils.password import hash_password


def test_login_success(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "TestUser123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert len(body["access_token"]) > 0
    assert isinstance(body["expires_in"], int)


def test_login_invalid_password(client: TestClient, test_user: User) -> None:
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "WrongPassword!"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


def test_login_unknown_user(client: TestClient) -> None:
    response = client.post(
        "/login",
        json={"username": "nobody", "password": "SomePassword1!"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}


def test_login_validation_missing_fields(client: TestClient) -> None:
    response = client.post("/login", json={})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation Error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["detail"] == "Validation Error"
    assert isinstance(body["errors"], list)
    assert len(body["errors"]) >= 2


def test_login_validation_empty_strings(client: TestClient) -> None:
    response = client.post("/login", json={"username": "", "password": ""})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_protected_endpoint_requires_auth(client: TestClient) -> None:
    response = client.get("/protected-endpoint")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_protected_endpoint_rejects_invalid_token(client: TestClient) -> None:
    response = client.get(
        "/protected-endpoint",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid authentication credentials"}


def test_protected_endpoint_accepts_valid_token(
    client: TestClient,
    test_user: User,
) -> None:
    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "TestUser123!"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        "/protected-endpoint",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"user": str(test_user.id)}


def test_duplicate_user_email_conflict(db_session: Session) -> None:
    first = User(
        username="user_one",
        email="duplicate@example.com",
        password_hash=hash_password("Password123!"),
    )
    duplicate = User(
        username="user_two",
        email="duplicate@example.com",
        password_hash=hash_password("Password123!"),
    )
    db_session.add(first)
    db_session.commit()

    db_session.add(duplicate)
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()

    db_session.delete(first)
    db_session.commit()
