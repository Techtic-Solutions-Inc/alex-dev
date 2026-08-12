import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import hash_password


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient) -> None:
    email = f"signup-success-{uuid.uuid4()}@example.com"
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "password": "securePassword123",
            "terms_accepted": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body == {
        "success": True,
        "message": "Account created successfully",
        "data": {
            "id": body["data"]["id"],
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
        },
    }
    assert body["data"]["id"]


@pytest.mark.asyncio
async def test_signup_email_already_in_use(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"duplicate-{uuid.uuid4()}@example.com"
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, is_locked) "
            "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false)"
        ),
        {
            "id": uuid.uuid4(),
            "username": email,
            "email": email,
            "first_name": "Jane",
            "last_name": "Doe",
            "hashed_password": hash_password("securePassword123"),
        },
    )
    db_session.flush()

    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "password": "securePassword123",
            "terms_accepted": True,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "An account with this email already exists"
    assert body["error"] == {
        "code": "EMAIL_ALREADY_EXISTS",
        "details": None,
    }


@pytest.mark.asyncio
async def test_signup_missing_fields(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "",
            "last_name": "Doe",
            "email": "",
            "password": "",
            "terms_accepted": True,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert {"first_name", "email", "password"}.issubset(field_names)


@pytest.mark.asyncio
async def test_signup_terms_not_accepted(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": f"terms-{uuid.uuid4()}@example.com",
            "password": "securePassword123",
            "terms_accepted": False,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    terms_errors = [
        item
        for item in body["error"]["details"]
        if item["field"] == "terms_accepted"
    ]
    assert len(terms_errors) == 1
    assert "You must accept the Terms of Use and Privacy Policy" in terms_errors[0]["message"]


@pytest.mark.asyncio
async def test_signup_weak_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": f"weak-{uuid.uuid4()}@example.com",
            "password": "12345678",
            "terms_accepted": True,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    password_errors = [
        item for item in body["error"]["details"] if item["field"] == "password"
    ]
    assert len(password_errors) == 1
    assert "Password must contain at least one letter" in password_errors[0]["message"]
