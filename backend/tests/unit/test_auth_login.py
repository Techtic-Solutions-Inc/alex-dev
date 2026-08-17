"""API tests for login and refresh session endpoints."""

from httpx import AsyncClient

from test_helpers import signup_payload


async def test_login_success(client: AsyncClient) -> None:
    signup = await client.post("/api/v1/auth/signup", json=signup_payload())
    assert signup.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "john.doe@example.com", "password": "StrongPassword123!"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Signed in successfully."
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]
    assert body["data"]["token_type"] == "bearer"
    assert body["data"]["user"]["email"] == "john.doe@example.com"


async def test_login_invalid_password(client: AsyncClient) -> None:
    signup = await client.post("/api/v1/auth/signup", json=signup_payload())
    assert signup.status_code == 201

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "john.doe@example.com", "password": "WrongPassword123!"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"
    assert body["message"] == "Email or password is incorrect."


async def test_login_unknown_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "StrongPassword123!"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_validation_error_returns_400(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "short"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


async def test_login_inactive_account(client: AsyncClient, test_db) -> None:
    signup = await client.post("/api/v1/auth/signup", json=signup_payload())
    assert signup.status_code == 201
    test_db["users"].update_one(
        {"email": "john.doe@example.com"},
        {"$set": {"is_active": False}},
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "john.doe@example.com", "password": "StrongPassword123!"},
    )

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ACCOUNT_INACTIVE"


async def test_refresh_rotates_session(client: AsyncClient) -> None:
    signup = await client.post("/api/v1/auth/signup", json=signup_payload())
    assert signup.status_code == 201
    refresh_token = signup.json()["data"]["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"] != refresh_token


async def test_refresh_rejects_reused_token(client: AsyncClient) -> None:
    signup = await client.post("/api/v1/auth/signup", json=signup_payload())
    refresh_token = signup.json()["data"]["refresh_token"]

    first = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert first.status_code == 200

    second = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert second.status_code == 401
    body = second.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_REFRESH_TOKEN"
