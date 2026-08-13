import uuid
from datetime import date

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
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def admin_id() -> str:
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_list_announcements_success(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
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
    assert body["data"]["page"] == 1
    assert body["data"]["limit"] == 20
    assert len(body["data"]["items"]) >= 1
    item = body["data"]["items"][0]
    assert item["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert item["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert item["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]


@pytest.mark.asyncio
async def test_filter_announcements_by_date(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    assert create_response.status_code == 201

    today = date.today().isoformat()
    response = await client.get(
        f"/api/announcements?date={today}",
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] >= 1
    assert len(body["data"]["items"]) >= 1

    future_date = "2099-12-31"
    empty_response = await client.get(
        f"/api/announcements?date={future_date}",
        headers=auth_header(user_id, role="user"),
    )
    assert empty_response.status_code == 200
    empty_body = empty_response.json()
    assert empty_body["data"]["total"] == 0
    assert empty_body["data"]["items"] == []


@pytest.mark.asyncio
async def test_unauthorized_create_announcement(
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
    assert body["data"]["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert body["data"]["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert body["data"]["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]
    assert body["data"]["privacy_policy_accepted"] is True
    assert body["data"]["terms_of_service_accepted"] is True
    assert body["data"]["id"]


@pytest.mark.asyncio
async def test_get_announcement_success(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
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
    assert body["data"]["id"] == announcement_id
    assert body["data"]["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert body["data"]["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert body["data"]["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]


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

    response = await client.put(
        f"/api/announcements/{announcement_id}",
        json={
            "title": "Updated Announcement Title",
            "body": "Updated announcement body text",
            "highlights": ["Updated highlight 1"],
        },
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Announcement updated successfully"
    assert body["data"]["title"] == "Updated Announcement Title"
    assert body["data"]["body"] == "Updated announcement body text"
    assert body["data"]["highlights"] == ["Updated highlight 1"]


@pytest.mark.asyncio
async def test_delete_announcement_success(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    announcement_id = create_response.json()["data"]["id"]

    delete_response = await client.delete(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(admin_id, role="admin"),
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(user_id, role="user"),
    )
    assert get_response.status_code == 404
    body = get_response.json()
    assert body["error"]["code"] == "ANNOUNCEMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_announcement_without_consent(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/announcements",
        json={
            **VALID_ANNOUNCEMENT_PAYLOAD,
            "privacy_policy_accepted": False,
            "terms_of_service_accepted": False,
        },
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "privacy_policy_accepted" in field_names
    assert "terms_of_service_accepted" in field_names


@pytest.mark.asyncio
async def test_get_announcement_requires_auth(client: AsyncClient) -> None:
    missing_id = str(uuid.uuid4())
    response = await client.get(f"/api/announcements/{missing_id}")
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
