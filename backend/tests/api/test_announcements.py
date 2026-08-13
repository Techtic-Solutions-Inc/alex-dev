
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

@pytest.mark.asyncio
async def test_create_announcement_success(client: AsyncClient, admin_id: str) -> None:
    response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert data["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert data["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]

@pytest.mark.asyncio
async def test_get_announcement_success(client: AsyncClient, admin_id: str) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    announcement_id = create_response.json()["id"]

    response = await client.get(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(admin_id, role="admin"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == VALID_ANNOUNCEMENT_PAYLOAD["title"]
    assert data["body"] == VALID_ANNOUNCEMENT_PAYLOAD["body"]
    assert data["highlights"] == VALID_ANNOUNCEMENT_PAYLOAD["highlights"]

@pytest.mark.asyncio
async def test_create_announcement_missing_consent(client: AsyncClient, admin_id: str) -> None:
    payload = VALID_ANNOUNCEMENT_PAYLOAD.copy()
    payload["privacy_policy_accepted"] = False
    response = await client.post(
        "/api/announcements",
        json=payload,
        headers=auth_header(admin_id, role="admin"),
    )
    assert response.status_code == 400
    assert "You must accept the Privacy Policy" in response.text

@pytest.mark.asyncio
async def test_update_announcement_success(client: AsyncClient, admin_id: str) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    announcement_id = create_response.json()["id"]

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
    data = response.json()
    assert data["title"] == update_payload["title"]
    assert data["body"] == update_payload["body"]
    assert data["highlights"] == update_payload["highlights"]

@pytest.mark.asyncio
async def test_delete_announcement_success(client: AsyncClient, admin_id: str) -> None:
    create_response = await client.post(
        "/api/announcements",
        json=VALID_ANNOUNCEMENT_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    announcement_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(admin_id, role="admin"),
    )
    assert response.status_code == 204

    get_response = await client.get(
        f"/api/announcements/{announcement_id}",
        headers=auth_header(admin_id, role="admin"),
    )
    assert get_response.status_code == 404
