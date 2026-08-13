import uuid

import pytest
from app.core.config import settings
from app.core.security import hash_password
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_signin_invalid_email_format(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "invalid-email",
            "password": "password123",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    email_errors = [
        item for item in body["error"]["details"] if item["field"] == "email"
    ]
    assert len(email_errors) == 1


@pytest.mark.asyncio
async def test_signin_incorrect_credentials(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Incorrect email or password"
    assert body["error"] == {
        "code": "INVALID_CREDENTIALS",
        "details": None,
    }


@pytest.mark.asyncio
async def test_signin_success(client: AsyncClient, db_session: Session) -> None:
    email = f"signin-success-{uuid.uuid4()}@example.com"
    password = "securePassword123"
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
            "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false, 'user')"
        ),
        {
            "id": uuid.uuid4(),
            "username": email,
            "email": email,
            "first_name": "John",
            "last_name": "Doe",
            "hashed_password": hash_password(password),
        },
    )
    db_session.flush()

    response = await client.post(
        "/api/auth/signin",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Signed in successfully"
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["expires_in"] == settings.JWT_EXPIRY * 60
    assert isinstance(body["data"]["access_token"], str)
    assert len(body["data"]["access_token"]) > 0


@pytest.mark.asyncio
async def test_signin_empty_fields(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "",
            "password": "",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert {"email", "password"}.issubset(field_names)


@pytest.mark.asyncio
async def test_signin_locked_account(client: AsyncClient, db_session: Session) -> None:
    email = f"locked-{uuid.uuid4()}@example.com"
    password = "securePassword123"
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
            "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, true, 'user')"
        ),
        {
            "id": uuid.uuid4(),
            "username": email,
            "email": email,
            "first_name": "Locked",
            "last_name": "User",
            "hashed_password": hash_password(password),
        },
    )
    db_session.flush()

    response = await client.post(
        "/api/auth/signin",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Your account has been locked. Please contact support."
    assert body["error"] == {
        "code": "ACCOUNT_LOCKED",
        "details": None,
    }


@pytest.mark.asyncio
async def test_signin_remember_me_extends_expiry(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"remember-{uuid.uuid4()}@example.com"
    password = "securePassword123"
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
            "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false, 'user')"
        ),
        {
            "id": uuid.uuid4(),
            "username": email,
            "email": email,
            "first_name": "Remember",
            "last_name": "Me",
            "hashed_password": hash_password(password),
        },
    )
    db_session.flush()

    response = await client.post(
        "/api/auth/signin",
        json={
            "email": email,
            "password": password,
            "remember_me": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["expires_in"] == settings.JWT_REMEMBER_ME_EXPIRY * 60
