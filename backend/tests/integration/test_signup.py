import uuid
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.main import app

SIGNUP_URL = "/api/auth/signup"
VALID_PAYLOAD = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
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


async def test_signup_success(db_client: AsyncClient) -> None:
    email = f"signup.success.{uuid.uuid4().hex[:8]}@example.com"
    payload = {**VALID_PAYLOAD, "email": email}

    response = await db_client.post(SIGNUP_URL, json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Account created successfully"
    assert body["data"]["first_name"] == payload["first_name"]
    assert body["data"]["last_name"] == payload["last_name"]
    assert body["data"]["email"] == email
    assert "password" not in body["data"]
    assert "hashed_password" not in body["data"]


async def test_signup_duplicate_email(db_client: AsyncClient) -> None:
    email = f"signup.duplicate.{uuid.uuid4().hex[:8]}@example.com"
    payload = {**VALID_PAYLOAD, "email": email}

    first = await db_client.post(SIGNUP_URL, json=payload)
    assert first.status_code == 201

    second = await db_client.post(SIGNUP_URL, json=payload)

    assert second.status_code == 400
    body = second.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"


async def test_signup_missing_fields(db_client: AsyncClient) -> None:
    response = await db_client.post(SIGNUP_URL, json={})

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
    assert len(body["error"]["details"]) > 0


async def test_signup_terms_not_accepted(db_client: AsyncClient) -> None:
    email = f"signup.terms.{uuid.uuid4().hex[:8]}@example.com"
    payload = {**VALID_PAYLOAD, "email": email, "terms_accepted": False}

    response = await db_client.post(SIGNUP_URL, json=payload)

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    terms_errors = [
        detail
        for detail in body["error"]["details"]
        if detail.get("field") == "terms_accepted"
    ]
    assert len(terms_errors) == 1
