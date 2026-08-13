import uuid

import pytest
from app.core.security import hash_password, verify_password
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.conftest import auth_header

_VALID_PROFILE = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "mobile_number": "1234567890",
    "bio": "This is my bio.",
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "country": "USA",
    },
    "time_zone": "GMT-4",
}


def _insert_user(
    db_session: Session,
    *,
    email: str,
    password: str = "securePassword123",
    first_name: str = "John",
    last_name: str = "Doe",
    mobile_number: str = "1234567890",
    bio: str = "This is my bio.",
    address_street: str = "123 Main St",
    address_city: str = "Anytown",
    address_state: str = "CA",
    address_zip: str = "12345",
    address_country: str = "USA",
    time_zone: str = "GMT-4",
) -> uuid.UUID:
    user_id = uuid.uuid4()
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, "
            "is_locked, role, mobile_number, bio, address_street, address_city, "
            "address_state, address_zip, address_country, time_zone) "
            "VALUES (:id, :username, :email, :first_name, :last_name, "
            ":hashed_password, false, 'user', :mobile_number, :bio, "
            ":address_street, :address_city, :address_state, :address_zip, "
            ":address_country, :time_zone)"
        ),
        {
            "id": user_id,
            "username": email,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "hashed_password": hash_password(password),
            "mobile_number": mobile_number,
            "bio": bio,
            "address_street": address_street,
            "address_city": address_city,
            "address_state": address_state,
            "address_zip": address_zip,
            "address_country": address_country,
            "time_zone": time_zone,
        },
    )
    db_session.flush()
    return user_id


@pytest.mark.asyncio
async def test_get_profile_success(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"profile-get-{uuid.uuid4()}@example.com"
    user_id = _insert_user(db_session, email=email)

    response = await client.get(
        "/api/profile",
        headers=auth_header(str(user_id)),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Profile retrieved successfully"
    assert body["data"] == {
        "first_name": "John",
        "last_name": "Doe",
        "email": email,
        "mobile_number": "1234567890",
        "bio": "This is my bio.",
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345",
            "country": "USA",
        },
        "time_zone": "GMT-4",
    }


@pytest.mark.asyncio
async def test_update_profile_success(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"profile-update-{uuid.uuid4()}@example.com"
    user_id = _insert_user(db_session, email=email)
    updated_email = f"updated-{uuid.uuid4()}@example.com"
    payload = {
        **_VALID_PROFILE,
        "email": updated_email,
        "first_name": "Jane",
        "last_name": "Smith",
        "mobile_number": "0987654321",
        "bio": "Updated bio.",
        "address": {
            "street": "456 Oak Ave",
            "city": "Othertown",
            "state": "NY",
            "zip": "67890",
            "country": "USA",
        },
        "time_zone": "GMT-5",
    }

    response = await client.put(
        "/api/profile",
        headers=auth_header(str(user_id)),
        json=payload,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Profile updated successfully"
    assert body["data"] == {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": updated_email,
        "mobile_number": "0987654321",
        "bio": "Updated bio.",
        "address": {
            "street": "456 Oak Ave",
            "city": "Othertown",
            "state": "NY",
            "zip": "67890",
            "country": "USA",
        },
        "time_zone": "GMT-5",
    }


@pytest.mark.asyncio
async def test_update_profile_missing_fields(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"profile-missing-{uuid.uuid4()}@example.com"
    user_id = _insert_user(db_session, email=email)

    response = await client.put(
        "/api/profile",
        headers=auth_header(str(user_id)),
        json={"first_name": "John"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(body["error"]["details"], list)
    missing_fields = {item["field"] for item in body["error"]["details"]}
    assert "last_name" in missing_fields
    assert "email" in missing_fields
    assert "mobile_number" in missing_fields
    assert "address" in missing_fields
    assert "time_zone" in missing_fields


@pytest.mark.asyncio
async def test_update_profile_unauthenticated(client: AsyncClient) -> None:
    response = await client.put("/api/profile", json=_VALID_PROFILE)

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_change_password_success(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"profile-pw-{uuid.uuid4()}@example.com"
    current_password = "securePassword123"
    new_password = "newSecurePassword456"
    user_id = _insert_user(db_session, email=email, password=current_password)

    response = await client.post(
        "/api/profile/change-password",
        headers=auth_header(str(user_id)),
        json={
            "current_password": current_password,
            "new_password": new_password,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Password changed successfully"
    assert body["data"]["id"] == str(user_id)

    row = db_session.execute(
        text("SELECT hashed_password FROM users WHERE id = :id"),
        {"id": user_id},
    ).one()
    assert verify_password(new_password, row[0])


@pytest.mark.asyncio
async def test_change_password_incorrect_current(
    client: AsyncClient,
    db_session: Session,
) -> None:
    email = f"profile-bad-pw-{uuid.uuid4()}@example.com"
    user_id = _insert_user(db_session, email=email, password="securePassword123")

    response = await client.post(
        "/api/profile/change-password",
        headers=auth_header(str(user_id)),
        json={
            "current_password": "wrongPassword123",
            "new_password": "newSecurePassword456",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Current password is incorrect"
    assert body["error"] == {
        "code": "INCORRECT_CURRENT_PASSWORD",
        "details": None,
    }
