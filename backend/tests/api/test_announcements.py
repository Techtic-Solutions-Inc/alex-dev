import uuid

import pytest
from httpx import AsyncClient
from tests.conftest import auth_header

VALID_ANNOUNCEMENT_PAYLOAD = {
    "title": "Announcement Title",
    "body": "Announcement body text",
    "highlights": [
        "Highlight 1",
        "Highlight 2",
        "Highlight 3",
    ],
    "privacy_policy_accepted": True,
    "terms_of_service_accepted": True,
}


@pytest.fixture
def admin_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_list_announcements_success(
    client: AsyncClient,
    admin_id: str,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    assert create_response.status_code == 201

    response = await client.get(
        "/api/announcements",
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Announcements retrieved successfully"
    assert body["data"]["total"] >= 1
    assert len(body["data"]["items"]) >= 1
    item = body["data"]["items"][0]
    assert item["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert item["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert item["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]


@pytest.mark.asyncio
async def test_create_announcement_success(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Announcement created successfully"
    data = body["data"]
    assert data["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert data["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert data["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]
    assert data["privacy_policy_accepted"] is True
    assert data["terms_of_service_accepted"] is True
    assert data["id"]


@pytest.mark.asyncio
async def test_get_announcement_success(
    client: AsyncClient,
    admin_id: str,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    announcement_id = create_response.json()["data"]["id"]

    response = await client.get(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Announcement retrieved successfully"
    data = body["data"]
    assert data["id"] == announcement_id
    assert data["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert data["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert data["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]


@pytest.mark.asyncio
async def test_create_announcement_missing_consent(
    client: AsyncClient,
    admin_id: str,
) -> None:
    payload = VALID_ANNOUNCEMENT_PAYLOAD.copy()
    payload["privacy_policy_accepted"] = False
    response = await client.post(
        "/api/announcements",
        json=payload,
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "privacy_policy_accepted" in field_names


@pytest.mark.asyncio
async def test_create_announcement_missing_fields(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/announcements",
        json={"title": "", "body": "", "highlights": []},
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_announcement_requires_admin(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 403
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_create_announcement_unauthorized(client: AsyncClient) -> None:
    response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_update_announcement_success(
    client: AsyncClient,
    admin_id: str,
) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    announcement_id = create_response.json()["data"]["id"]

    update_payload = {
        "title": "Updated Title",
        "body": "Updated body text",
        "highlights": ["Updated highlight 1"],
    }
    response = await client.put(
        f"/api/announcements/{announcement_id}",
        json=update_payload,
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Announcement updated successfully"
    data = body["data"]
    assert data["title"] == update_payload["title"]
    assert data["body"] == update_payload["body"]
    assert data["highlights"] == update_payload["highlights"]


@pytest.mark.asyncio
async def test_update_announcement_not_found(
    client: AsyncClient,
    admin_id: str,
) -> None:
    missing_id = str(uuid.uuid4())
    response = await client.put(
        f"/api/announcements/{missing_id}",
        json={"title": "Updated Title"},
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ANNOUNCEMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_announcement_success(
    client: AsyncClient,
    admin_id: str,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    announcement_id = create_response.json()["data"]["id"]

    response = await client.delete(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(admin_id, role="admin"),
    )
    assert response.status_code == 204
    assert response.content == b""

    get_response = await client.get(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(user_id, role="user"),
    )
    assert get_response.status_code == 404
    body = get_response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "ANNOUNCEMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_list_announcements_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/announcements")

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"
