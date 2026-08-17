"""Integration tests for the signup endpoint."""

from httpx import AsyncClient

from test_helpers import signup_payload


async def test_signup_success(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/signup", json=signup_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Account created successfully."
    assert body["data"]["email"] == "john.doe@example.com"
    assert body["data"]["first_name"] == "John"
    assert body["data"]["last_name"] == "Doe"
    assert body["data"]["email_verified"] is False
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]
    assert body["data"]["token_type"] == "bearer"


async def test_signup_missing_terms(client: AsyncClient) -> None:
    payload = signup_payload()
    del payload["terms_accepted"]
    response = await client.post("/api/v1/auth/signup", json=payload)

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "terms_accepted" in body["error"]["details"]


async def test_signup_duplicate_email(client: AsyncClient) -> None:
    first = await client.post("/api/v1/auth/signup", json=signup_payload())
    assert first.status_code == 201

    response = await client.post(
        "/api/v1/auth/signup",
        json=signup_payload(email="john.doe@example.com"),
    )

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "EMAIL_ALREADY_EXISTS"
    assert "email" in body["error"]["details"]


async def test_signup_weak_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/signup",
        json=signup_payload(password="weak"),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "password" in body["error"]["details"]


async def test_signup_terms_not_accepted(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/signup",
        json=signup_payload(terms_accepted=False),
    )

    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "terms_accepted" in body["error"]["details"]
