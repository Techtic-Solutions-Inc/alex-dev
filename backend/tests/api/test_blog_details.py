import uuid

import pytest
from httpx import AsyncClient
from tests.conftest import auth_header

VALID_BLOG_DETAILS_PAYLOAD = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "1234567890",
    "message": "This is a sample message.",
    "privacy_policy_accepted": True,
    "terms_of_service_accepted": True,
}


@pytest.fixture
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_blog_details_success(client: AsyncClient) -> None:
    response = await client.get("/api/blog/details")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Blog details retrieved successfully"
    assert body["data"]["link"] == "/api/blog/details"
    page = body["data"]["page"]
    assert page["content"]
    assert len(page["headings"]) >= 1
    assert page["headings"][0]["text"]
    assert page["headings"][0]["level"] >= 1
    assert len(page["sections"]) >= 1
    assert page["sections"][0]["heading"]
    assert page["sections"][0]["text"]
    assert page["additional_info"]


@pytest.mark.asyncio
async def test_create_blog_details_success(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/blog/details",
        json=VALID_BLOG_DETAILS_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Blog details submitted successfully"
    assert body["data"]["first_name"] == VALID_BLOG_DETAILS_PAYLOAD["first_name"]
    assert body["data"]["last_name"] == VALID_BLOG_DETAILS_PAYLOAD["last_name"]
    assert body["data"]["email"] == VALID_BLOG_DETAILS_PAYLOAD["email"]
    assert body["data"]["phone_number"] == VALID_BLOG_DETAILS_PAYLOAD["phone_number"]
    assert body["data"]["message"] == VALID_BLOG_DETAILS_PAYLOAD["message"]
    assert body["data"]["id"]


@pytest.mark.asyncio
async def test_create_blog_details_invalid_email(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/blog/details",
        json={
            **VALID_BLOG_DETAILS_PAYLOAD,
            "email": "not-an-email",
        },
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "email" in field_names


@pytest.mark.asyncio
async def test_create_blog_details_missing_fields(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/blog/details",
        json={
            "first_name": "",
            "last_name": "",
            "email": "",
            "phone_number": "",
            "message": "",
            "privacy_policy_accepted": True,
            "terms_of_service_accepted": True,
        },
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert {"first_name", "last_name", "email", "phone_number", "message"}.issubset(
        field_names
    )


@pytest.mark.asyncio
async def test_create_blog_details_without_consent(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/blog/details",
        json={
            **VALID_BLOG_DETAILS_PAYLOAD,
            "privacy_policy_accepted": False,
            "terms_of_service_accepted": False,
        },
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "privacy_policy_accepted" in field_names
    assert "terms_of_service_accepted" in field_names


@pytest.mark.asyncio
async def test_create_blog_details_excessively_long_input(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/blog/details",
        json={
            **VALID_BLOG_DETAILS_PAYLOAD,
            "message": "x" * 5001,
        },
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_blog_details_sql_injection(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/blog/details",
        json={
            **VALID_BLOG_DETAILS_PAYLOAD,
            "message": "'; DROP TABLE blog_details; --",
        },
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_update_blog_details_success(
    client: AsyncClient,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/blog/details",
        json=VALID_BLOG_DETAILS_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    detail_id = create_response.json()["data"]["id"]

    response = await client.put(
        f"/api/blog/details/{detail_id}",
        json={"message": "Updated message text."},
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Blog details updated successfully"
    assert body["data"]["message"] == "Updated message text."


@pytest.mark.asyncio
async def test_update_blog_details_missing_fields(
    client: AsyncClient,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/blog/details",
        json=VALID_BLOG_DETAILS_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    detail_id = create_response.json()["data"]["id"]

    response = await client.put(
        f"/api/blog/details/{detail_id}",
        json={},
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_delete_blog_details_success(
    client: AsyncClient,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/blog/details",
        json=VALID_BLOG_DETAILS_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )
    detail_id = create_response.json()["data"]["id"]

    delete_response = await client.delete(
        f"/api/blog/details/{detail_id}",
        headers=auth_header(user_id, role="user"),
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""


@pytest.mark.asyncio
async def test_create_blog_details_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/blog/details",
        json=VALID_BLOG_DETAILS_PAYLOAD,
    )

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
