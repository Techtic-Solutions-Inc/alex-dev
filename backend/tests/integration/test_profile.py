import pytest
from httpx import AsyncClient

from app.main import app
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_get_profile_happy_path(async_client: AsyncClient, user_token_headers):
    response = await async_client.get("/api/profile", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'first_name' in data['data']
    assert 'last_name' in data['data']

@pytest.mark.asyncio
async def test_update_profile_happy_path(async_client: AsyncClient, user_token_headers):
    update_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "mobile_number": "0987654321",
        "bio": "Updated bio.",
        "address": {
            "street": "456 Elm St",
            "city": "Othertown",
            "state": "NY",
            "zip": "54321",
            "country": "USA"
        },
        "time_zone": "GMT-5"
    }
    response = await async_client.put("/api/profile", json=update_data, headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert data['data']['first_name'] == "Jane"

@pytest.mark.asyncio
async def test_update_profile_missing_fields(async_client: AsyncClient, user_token_headers):
    update_data = {
        "first_name": "",
        "last_name": "Doe"
    }
    response = await async_client.put("/api/profile", json=update_data, headers=user_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert data['message'] == "Validation error"

@pytest.mark.asyncio
async def test_update_profile_unauthenticated(async_client: AsyncClient):
    update_data = {
        "first_name": "Jane",
        "last_name": "Doe"
    }
    response = await async_client.put("/api/profile", json=update_data)
    assert response.status_code == 401
    data = response.json()
    assert data['success'] is False
    assert data['message'] == "Authentication required"

@pytest.mark.asyncio
async def test_change_password_happy_path(async_client: AsyncClient, user_token_headers):
    change_password_data = {
        "current_password": "TestUser123!",
        "new_password": "NewPassword123!"
    }
    response = await async_client.post("/api/profile/change-password", json=change_password_data, headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True

@pytest.mark.asyncio
async def test_change_password_incorrect_current(async_client: AsyncClient, user_token_headers):
    change_password_data = {
        "current_password": "WrongPassword",
        "new_password": "NewPassword123!"
    }
    response = await async_client.post("/api/profile/change-password", json=change_password_data, headers=user_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert data['success'] is False
    assert data['message'] == "Current password is incorrect"
