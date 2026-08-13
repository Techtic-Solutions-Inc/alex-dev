import uuid

import pytest
from httpx import AsyncClient
from tests.conftest import auth_header

VALID_BLOG_PAYLOAD = {
    "title": "Hates to see me coming",
    "content": (
        "Lorem Ipsum has been the industry's standard dummy text ever since "
        "the 1500s, when an unknown printer took a galley of type and "
        "scrambled it to make a type specimen book."
    ),
    "terms_accepted": True,
    "phone": "+1-555-0100",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
}


@pytest.fixture
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def admin_id() -> str:
    return str(uuid.uuid4())


@pytest.mark.asyncio
async def test_get_blog_posts(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
) -> None:
    create_response = await client.post(
        "/api/blog",
        json=VALID_BLOG_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    assert create_response.status_code == 201

    response = await client.get(
        "/api/blog",
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Blog posts retrieved successfully"
    assert body["data"]["total"] >= 1
    assert len(body["data"]["items"]) >= 1
    item = body["data"]["items"][0]
    assert item["title"] == VALID_BLOG_PAYLOAD["title"]
    assert item["phone"] == VALID_BLOG_PAYLOAD["phone"]
    assert item["phone_number"] == VALID_BLOG_PAYLOAD["phone"]
    assert item["terms_accepted"] is True
    assert item["first_name"] == VALID_BLOG_PAYLOAD["first_name"]
    assert item["last_name"] == VALID_BLOG_PAYLOAD["last_name"]
    assert item["email"] == VALID_BLOG_PAYLOAD["email"]
    assert item["name"] == "Jane Smith"
    assert item["link"].startswith("/api/blog/")


@pytest.mark.asyncio
async def test_create_blog_post(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/blog",
        json=VALID_BLOG_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Blog post created successfully"
    assert body["data"]["title"] == VALID_BLOG_PAYLOAD["title"]
    assert body["data"]["content"] == VALID_BLOG_PAYLOAD["content"]
    assert body["data"]["phone"] == VALID_BLOG_PAYLOAD["phone"]
    assert body["data"]["id"]


@pytest.mark.asyncio
async def test_create_blog_post_missing_fields(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/blog",
        json={
            "title": "",
            "content": "",
            "terms_accepted": True,
        },
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert {"title", "content", "phone"}.issubset(field_names)


@pytest.mark.asyncio
async def test_create_blog_post_terms_not_accepted(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/blog",
        json={
            **VALID_BLOG_PAYLOAD,
            "terms_accepted": False,
        },
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    terms_errors = [
        item
        for item in body["error"]["details"]
        if item["field"] == "terms_accepted"
    ]
    assert len(terms_errors) == 1
    assert "You must accept the Terms of Use and Privacy Policy" in terms_errors[0]["message"]


@pytest.mark.asyncio
async def test_create_blog_post_terms_omitted(
    client: AsyncClient,
    admin_id: str,
) -> None:
    payload = {k: v for k, v in VALID_BLOG_PAYLOAD.items() if k != "terms_accepted"}
    response = await client.post(
        "/api/blog",
        json=payload,
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_update_blog_post(
    client: AsyncClient,
    admin_id: str,
) -> None:
    create_response = await client.post(
        "/api/blog",
        json=VALID_BLOG_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    blog_id = create_response.json()["data"]["id"]

    response = await client.put(
        f"/api/blog/{blog_id}",
        json={"title": "Updated blog title", "content": "Updated content."},
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Blog post updated successfully"
    assert body["data"]["title"] == "Updated blog title"
    assert body["data"]["content"] == "Updated content."


@pytest.mark.asyncio
async def test_delete_blog_post(
    client: AsyncClient,
    admin_id: str,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/blog",
        json=VALID_BLOG_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    blog_id = create_response.json()["data"]["id"]

    delete_response = await client.delete(
        f"/api/blog/{blog_id}",
        headers=auth_header(admin_id, role="admin"),
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get(
        f"/api/blog/{blog_id}",
        headers=auth_header(user_id, role="user"),
    )
    assert get_response.status_code == 404
    body = get_response.json()
    assert body["error"]["code"] == "BLOG_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_blog_post_by_id(
    client: AsyncClient,
    admin_id: str,
    user_id: str,
) -> None:
    create_response = await client.post(
        "/api/blog",
        json=VALID_BLOG_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    blog_id = create_response.json()["data"]["id"]

    response = await client.get(
        f"/api/blog/{blog_id}",
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == blog_id
    assert body["data"]["title"] == VALID_BLOG_PAYLOAD["title"]
    assert body["data"]["description"]
    assert body["data"]["link"] == f"/api/blog/{blog_id}"


@pytest.mark.asyncio
async def test_get_blog_post_not_found(
    client: AsyncClient,
    user_id: str,
) -> None:
    missing_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/blog/{missing_id}",
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Blog post not found"
    assert body["error"]["code"] == "BLOG_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_blog_post_requires_admin(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.post(
        "/api/blog",
        json=VALID_BLOG_PAYLOAD,
        headers=auth_header(user_id, role="user"),
    )

    assert response.status_code == 403
    body = response.json()
    assert body["error"]["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_get_blog_posts_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/blog")
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
