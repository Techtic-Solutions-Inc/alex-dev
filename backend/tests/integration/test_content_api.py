import uuid

import pytest
from httpx import AsyncClient
from tests.conftest import auth_header

VALID_CONTENT_PAYLOAD = {
    "caption": "Hates to see me coming",
    "terms_accepted": True,
    "privacy_policy": True,
    "phone": "+1-555-0100",
    "full_name": "Joseph",
}


@pytest.fixture
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_create_content(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/content",
        json=VALID_CONTENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Content created successfully"
    assert body["data"]["caption"] == VALID_CONTENT_PAYLOAD["caption"]
    assert body["data"]["terms_accepted"] is True
    assert body["data"]["privacy_policy"] is True
    assert body["data"]["phone"] == VALID_CONTENT_PAYLOAD["phone"]
    assert body["data"]["full_name"] == "Joseph"
    assert body["data"]["description"]
    assert body["data"]["link"].startswith("/api/content/")
    assert body["data"]["error"] is None
    assert body["data"]["id"]


@pytest.mark.asyncio
async def test_create_content_missing_fields(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/content",
        json={"phone": "+1-555-0100"},
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "caption" in field_names
    assert "terms_accepted" in field_names


@pytest.mark.asyncio
async def test_create_content_duplicate_caption(
    client: AsyncClient,
    user_id: str,
) -> None:
    first = await client.post(
        "/api/content",
        json=VALID_CONTENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    assert first.status_code == 201

    response = await client.post(
        "/api/content",
        json=VALID_CONTENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Content with this caption already exists"
    assert body["error"]["code"] == "CONTENT_CAPTION_ALREADY_EXISTS"


@pytest.mark.asyncio
async def test_get_content_by_id(
    client: AsyncClient,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/content",
        json=VALID_CONTENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    content_id = create_response.json()["data"]["id"]

    response = await client.get(f"/api/content/{content_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Content retrieved successfully"
    assert body["data"]["id"] == content_id
    assert body["data"]["caption"] == VALID_CONTENT_PAYLOAD["caption"]
    assert body["data"]["phone"] == VALID_CONTENT_PAYLOAD["phone"]
    assert body["data"]["description"]
    assert body["data"]["link"] == f"/api/content/{content_id}"
    assert body["data"]["error"] is None


@pytest.mark.asyncio
async def test_get_content_not_found(client: AsyncClient) -> None:
    missing_id = str(uuid.uuid4())
    response = await client.get(f"/api/content/{missing_id}")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Content not found"
    assert body["error"]["code"] == "CONTENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_update_content(
    client: AsyncClient,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/content",
        json=VALID_CONTENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    content_id = create_response.json()["data"]["id"]

    response = await client.put(
        f"/api/content/{content_id}",
        json={"caption": "Updated caption", "phone": "+1-555-0199"},
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Content updated successfully"
    assert body["data"]["caption"] == "Updated caption"
    assert body["data"]["phone"] == "+1-555-0199"


@pytest.mark.asyncio
async def test_update_content_invalid_data(
    client: AsyncClient,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/content",
        json=VALID_CONTENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    content_id = create_response.json()["data"]["id"]

    response = await client.put(
        f"/api/content/{content_id}",
        json={"caption": ""},
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "caption" in field_names


@pytest.mark.asyncio
async def test_create_content_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/api/content", json=VALID_CONTENT_PAYLOAD)
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_update_content_requires_auth(
    client: AsyncClient,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/content",
        json=VALID_CONTENT_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    content_id = create_response.json()["data"]["id"]

    response = await client.put(
        f"/api/content/{content_id}",
        json={"caption": "No auth update"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_create_content_terms_not_accepted(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/content",
        json={
            **VALID_CONTENT_PAYLOAD,
            "terms_accepted": False,
        },
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    terms_errors = [
        item
        for item in body["error"]["details"]
        if item["field"] == "terms_accepted"
    ]
    assert len(terms_errors) == 1
