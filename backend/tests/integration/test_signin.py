import uuid
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.dependencies.db import get_db
from app.main import app

SIGNIN_URL = "/api/auth/signin"
SIGNUP_URL = "/api/auth/signup"
VALID_SIGNUP_PAYLOAD = {
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "password": "securePassword123",
    "terms_accepted": True,
}


@pytest.fixture
async def db_client(db_session: Session) -> AsyncIterator[AsyncClient]:
    """HTTP client with database session override for isolated tests."""

    def override_get_db() -> Session:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


async def _register_user(
    client: AsyncClient,
    email: str,
    password: str = "securePassword123",
) -> None:
    payload = {
        **VALID_SIGNUP_PAYLOAD,
        "email": email,
        "password": password,
    }
    response = await client.post(SIGNUP_URL, json=payload)
    assert response.status_code == 201


async def test_signin_success(db_client: AsyncClient) -> None:
    email = f"signin.success.{uuid.uuid4().hex[:8]}@example.com"
    password = "securePassword123"
    await _register_user(db_client, email, password)

    response = await db_client.post(
        SIGNIN_URL,
        json={"email": email, "password": password, "remember_me": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Signed in successfully"
    assert body["data"]["token_type"] == "bearer"
    assert isinstance(body["data"]["access_token"], str)
    assert len(body["data"]["access_token"]) > 0
    assert body["data"]["expires_in"] == settings.JWT_EXPIRY * 60


async def test_signin_invalid_email_format(db_client: AsyncClient) -> None:
    response = await db_client.post(
        SIGNIN_URL,
        json={
            "email": "not-an-email",
            "password": "password123",
            "remember_me": False,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    email_errors = [
        detail
        for detail in body["error"]["details"]
        if detail.get("field") == "email"
    ]
    assert len(email_errors) >= 1


async def test_signin_incorrect_credentials(db_client: AsyncClient) -> None:
    email = f"signin.bad.{uuid.uuid4().hex[:8]}@example.com"
    await _register_user(db_client, email)

    response = await db_client.post(
        SIGNIN_URL,
        json={
            "email": email,
            "password": "wrongPassword123",
            "remember_me": False,
        },
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"
    assert body["message"] == "Incorrect email or password"


async def test_signin_unknown_email(db_client: AsyncClient) -> None:
    response = await db_client.post(
        SIGNIN_URL,
        json={
            "email": f"unknown.{uuid.uuid4().hex[:8]}@example.com",
            "password": "securePassword123",
            "remember_me": False,
        },
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


async def test_signin_remember_me(db_client: AsyncClient) -> None:
    email = f"signin.remember.{uuid.uuid4().hex[:8]}@example.com"
    password = "securePassword123"
    await _register_user(db_client, email, password)

    standard_response = await db_client.post(
        SIGNIN_URL,
        json={"email": email, "password": password, "remember_me": False},
    )
    remember_response = await db_client.post(
        SIGNIN_URL,
        json={"email": email, "password": password, "remember_me": True},
    )

    assert standard_response.status_code == 200
    assert remember_response.status_code == 200

    standard_expires = standard_response.json()["data"]["expires_in"]
    remember_expires = remember_response.json()["data"]["expires_in"]

    assert standard_expires == settings.JWT_EXPIRY * 60
    assert remember_expires == settings.JWT_REMEMBER_ME_EXPIRY * 60
    assert remember_expires > standard_expires


async def test_signin_empty_fields(db_client: AsyncClient) -> None:
    response = await db_client.post(
        SIGNIN_URL,
        json={"email": "", "password": "", "remember_me": False},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
    assert len(body["error"]["details"]) > 0
