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


VALID_TEMPLATE_PAYLOAD = {
    "title": "Open House Flyer",
    "description": "A professional open house marketing template",
    "status": "active",
}


@pytest.fixture
def user_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def admin_id() -> str:
    return str(uuid.uuid4())


async def _create_template(
    client: AsyncClient,
    admin_id: str,
    payload: dict | None = None,
) -> dict:
    response = await client.post(
        "/api/content-library",
        json=payload or VALID_TEMPLATE_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )
    assert response.status_code == 201
    return response.json()["data"]


@pytest.mark.asyncio
async def test_list_content_templates_success(
    client: AsyncClient,
    admin_id: str,
) -> None:
    await _create_template(client, admin_id)

    response = await client.get("/api/content-library")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Content templates retrieved successfully"
    assert body["data"]["total"] >= 1
    assert body["data"]["page"] == 1
    assert body["data"]["limit"] == 20
    assert len(body["data"]["items"]) >= 1
    item = body["data"]["items"][0]
    assert item["status"] == "active"
    assert "id" in item
    assert "title" in item
    assert "description" in item


@pytest.mark.asyncio
async def test_list_content_templates_only_active(
    client: AsyncClient,
    admin_id: str,
) -> None:
    active_payload = {
        **VALID_TEMPLATE_PAYLOAD,
        "title": f"Active Template {uuid.uuid4()}",
        "status": "active",
    }
    inactive_payload = {
        **VALID_TEMPLATE_PAYLOAD,
        "title": f"Inactive Template {uuid.uuid4()}",
        "status": "inactive",
    }
    await _create_template(client, admin_id, active_payload)
    await _create_template(client, admin_id, inactive_payload)

    response = await client.get("/api/content-library")

    assert response.status_code == 200
    items = response.json()["data"]["items"]
    assert all(item["status"] == "active" for item in items)
    titles = {item["title"] for item in items}
    assert active_payload["title"] in titles
    assert inactive_payload["title"] not in titles


@pytest.mark.asyncio
async def test_list_content_templates_pagination(
    client: AsyncClient,
    admin_id: str,
) -> None:
    for index in range(3):
        await _create_template(
            client,
            admin_id,
            {
                **VALID_TEMPLATE_PAYLOAD,
                "title": f"Paginated Template {uuid.uuid4()} {index}",
            },
        )

    response = await client.get(
        "/api/content-library",
        params={"page": 1, "limit": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["page"] == 1
    assert body["data"]["limit"] == 2
    assert len(body["data"]["items"]) == 2
    assert body["data"]["total"] >= 3


@pytest.mark.asyncio
async def test_search_content_templates(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
) -> None:
    unique_title = f"Searchable Flyer {uuid.uuid4()}"
    await _create_template(
        client,
        admin_id,
        {
            **VALID_TEMPLATE_PAYLOAD,
            "title": unique_title,
            "description": "Unique searchable description keyword",
        },
    )

    response = await client.get(
        "/api/content-library/search",
        params={"q": "searchable description"},
        headers=auth_header(user_id),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] >= 1
    assert any(unique_title in item["title"] for item in body["data"]["items"])


@pytest.mark.asyncio
async def test_search_content_templates_unauthorized(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/content-library/search",
        params={"q": "open house"},
    )

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_search_content_templates_invalid_query(
    client: AsyncClient,
    user_id: str,
) -> None:
    response = await client.get(
        "/api/content-library/search",
        params={"q": "   "},
        headers=auth_header(user_id),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_get_content_template_details(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
) -> None:
    created = await _create_template(client, admin_id)

    response = await client.get(
        f"/api/content-library/{created['id']}",
        headers=auth_header(user_id),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Content template retrieved successfully"
    assert body["data"]["id"] == created["id"]
    assert body["data"]["title"] == VALID_TEMPLATE_PAYLOAD["title"]
    assert body["data"]["description"] == VALID_TEMPLATE_PAYLOAD["description"]
    assert body["data"]["status"] == "active"


@pytest.mark.asyncio
async def test_get_content_template_not_found(
    client: AsyncClient,
    user_id: str,
) -> None:
    missing_id = str(uuid.uuid4())

    response = await client.get(
        f"/api/content-library/{missing_id}",
        headers=auth_header(user_id),
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "CONTENT_TEMPLATE_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_content_template_unauthorized(
    client: AsyncClient,
    admin_id: str,
) -> None:
    created = await _create_template(client, admin_id)

    response = await client.get(f"/api/content-library/{created['id']}")

    assert response.status_code == 401
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_create_content_template_success(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/content-library",
        json=VALID_TEMPLATE_PAYLOAD,
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Content template created successfully"
    assert body["data"]["title"] == VALID_TEMPLATE_PAYLOAD["title"]
    assert body["data"]["status"] == "active"
    assert body["data"]["id"]


@pytest.mark.asyncio
async def test_create_content_template_invalid_data(
    client: AsyncClient,
    admin_id: str,
) -> None:
    response = await client.post(
        "/api/content-library",
        json={"title": "   ", "status": "active"},
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_update_content_template_success(
    client: AsyncClient,
    admin_id: str,
) -> None:
    created = await _create_template(client, admin_id)

    response = await client.put(
        f"/api/content-library/{created['id']}",
        json={"title": "Updated Flyer Title", "status": "inactive"},
        headers=auth_header(admin_id, role="admin"),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Content template updated successfully"
    assert body["data"]["title"] == "Updated Flyer Title"
    assert body["data"]["status"] == "inactive"


@pytest.mark.asyncio
async def test_delete_content_template_success(
    client: AsyncClient,
    user_id: str,
    admin_id: str,
) -> None:
    created = await _create_template(client, admin_id)

    delete_response = await client.delete(
        f"/api/content-library/{created['id']}",
        headers=auth_header(admin_id, role="admin"),
    )
    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/content-library/{created['id']}",
        headers=auth_header(user_id),
    )
    assert get_response.status_code == 404
    body = get_response.json()
    assert body["error"]["code"] == "CONTENT_TEMPLATE_NOT_FOUND"
