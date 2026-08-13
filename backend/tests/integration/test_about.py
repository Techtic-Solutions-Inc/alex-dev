import pytest
from httpx import AsyncClient

VALID_ABOUT_PAYLOAD = {
    "phone": "+1-555-0100",
    "terms_accepted": True,
}

EXPECTED_TEAM_NAMES = {"Abby", "Cam", "Hunter", "Josh", "Nova"}


@pytest.mark.asyncio
async def test_get_about_success(client: AsyncClient) -> None:
    response = await client.request(
        "GET",
        "/api/about",
        json=VALID_ABOUT_PAYLOAD,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "About Us content retrieved successfully"

    data = body["data"]
    assert data["id"] == "about-us"
    assert data["link"] == "/api/about"
    assert data["description"]
    assert data["error"] is None
    assert data["phone"] == VALID_ABOUT_PAYLOAD["phone"]
    assert data["terms_accepted"] is True
    assert data["marketing_content"]
    assert isinstance(data["roles"], list)
    assert len(data["roles"]) >= 1

    team_members = data["team_members"]
    assert isinstance(team_members, list)
    assert len(team_members) == 5
    assert {member["name"] for member in team_members} == EXPECTED_TEAM_NAMES

    for member in team_members:
        assert member["id"]
        assert member["name"]
        assert member["role"]
        assert member["roles"]
        assert member["description"]
        assert member["link"].startswith("/api/about")
        assert member["error"] is None


@pytest.mark.asyncio
async def test_get_about_missing_fields(client: AsyncClient) -> None:
    response = await client.request("GET", "/api/about", json={})

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "phone" in field_names
    assert "terms_accepted" in field_names


@pytest.mark.asyncio
async def test_get_about_terms_not_accepted(client: AsyncClient) -> None:
    response = await client.request(
        "GET",
        "/api/about",
        json={
            "phone": "+1-555-0100",
            "terms_accepted": False,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["message"] == "Validation error"
    assert body["error"]["code"] == "VALIDATION_ERROR"
    terms_errors = [
        item
        for item in body["error"]["details"]
        if item["field"] == "terms_accepted"
    ]
    assert terms_errors
    assert "Terms of Use" in terms_errors[0]["message"]


@pytest.mark.asyncio
async def test_get_about_terms_omitted(client: AsyncClient) -> None:
    response = await client.request(
        "GET",
        "/api/about",
        json={"phone": "+1-555-0100"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    field_names = {item["field"] for item in body["error"]["details"]}
    assert "terms_accepted" in field_names


@pytest.mark.asyncio
async def test_get_about_invalid_phone(client: AsyncClient) -> None:
    response = await client.request(
        "GET",
        "/api/about",
        json={
            "phone": "abc",
            "terms_accepted": True,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"
    phone_errors = [
        item for item in body["error"]["details"] if item["field"] == "phone"
    ]
    assert phone_errors
