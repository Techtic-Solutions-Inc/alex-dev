import uuid

import pytest
from app.core.security import hash_password
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.conftest import auth_header


def _insert_user(
    db_session: Session,
    *,
    email: str,
    first_name: str = "John",
    last_name: str = "Doe",
    ai_credit_usage: int = 0,
    password: str = "securePassword123",
) -> uuid.UUID:
    user_id = uuid.uuid4()
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, "
            "is_locked, role, mobile_number, bio, address_street, address_city, "
            "address_state, address_zip, address_country, time_zone, "
            "ai_credit_usage) "
            "VALUES (:id, :username, :email, :first_name, :last_name, "
            ":hashed_password, false, 'user', '', '', '', '', '', '', '', '', "
            ":ai_credit_usage)"
        ),
        {
            "id": user_id,
            "username": email,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "hashed_password": hash_password(password),
            "ai_credit_usage": ai_credit_usage,
        },
    )
    db_session.flush()
    return user_id


@pytest.mark.asyncio
async def test_get_user_details_success(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"cl-user-{uuid.uuid4()}@example.com"
    user_id = _insert_user(
        db_session,
        email=email,
        first_name="Jane",
        last_name="Smith",
        ai_credit_usage=15,
    )

    response = await client.get(
        "/api/content-library/user-details",
        headers=auth_header(str(user_id)),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "User details retrieved successfully"
    assert body["data"] == {
        "user_id": str(user_id),
        "name": "Jane Smith",
        "ai_credit_usage": 15,
    }


@pytest.mark.asyncio
async def test_get_user_details_unauthorized(client: AsyncClient) -> None:
    response = await client.get("/api/content-library/user-details")

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_user_details_forbidden(
    client: AsyncClient,
    db_session: Session,
) -> None:
    """Users cannot retrieve another user's details (403)."""
    owner_email = f"cl-owner-{uuid.uuid4()}@example.com"
    other_email = f"cl-other-{uuid.uuid4()}@example.com"
    owner_id = _insert_user(db_session, email=owner_email, ai_credit_usage=3)
    other_id = _insert_user(
        db_session,
        email=other_email,
        first_name="Other",
        last_name="User",
        ai_credit_usage=99,
    )

    response = await client.get(
        "/api/content-library/user-details",
        params={"user_id": str(other_id)},
        headers=auth_header(str(owner_id)),
    )

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "You cannot access another user's details"
    assert body["error"]["code"] == "USER_DETAILS_FORBIDDEN"
    assert body["error"]["details"] is None


@pytest.mark.asyncio
async def test_get_user_details_forbidden_invalid_role(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"cl-role-{uuid.uuid4()}@example.com"
    user_id = _insert_user(db_session, email=email)

    response = await client.get(
        "/api/content-library/user-details",
        headers=auth_header(str(user_id), role="guest"),
    )

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_get_user_details_includes_name_and_ai_credit_usage(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"cl-content-{uuid.uuid4()}@example.com"
    user_id = _insert_user(
        db_session,
        email=email,
        first_name="Alex",
        last_name="Rivera",
        ai_credit_usage=7,
    )

    response = await client.get(
        "/api/content-library/user-details",
        headers=auth_header(str(user_id)),
        params={"user_id": str(user_id)},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert set(data.keys()) == {"user_id", "name", "ai_credit_usage"}
    assert data["user_id"] == str(user_id)
    assert data["name"] == "Alex Rivera"
    assert isinstance(data["ai_credit_usage"], int)
    assert data["ai_credit_usage"] == 7


@pytest.mark.asyncio
async def test_get_user_details_not_found(client: AsyncClient) -> None:
    missing_id = str(uuid.uuid4())

    response = await client.get(
        "/api/content-library/user-details",
        headers=auth_header(missing_id),
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "USER_NOT_FOUND"
