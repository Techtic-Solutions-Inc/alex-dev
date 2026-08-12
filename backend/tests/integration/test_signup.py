
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "securePassword123",
            "terms_accepted": True
        }
    )
    assert response.status_code == 201
    assert response.json()["success"] is True
    assert response.json()["message"] == "Account created successfully"
    assert "id" in response.json()["data"]


@pytest.mark.asyncio
async def test_signup_email_already_in_use(client: AsyncClient, db_session):
    # Pre-insert a user with the same email
    db_session.execute(
        """
        INSERT INTO users (username, email, first_name, last_name, hashed_password, is_locked)
        VALUES ('johndoe', 'john.doe@example.com', 'John', 'Doe', 'hashedpassword', false)
        """
    )
    db_session.commit()

    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "securePassword123",
            "terms_accepted": True
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already in use"


@pytest.mark.asyncio
async def test_signup_missing_fields(client: AsyncClient):
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "",
            "last_name": "Doe",
            "email": "",
            "password": "",
            "terms_accepted": True
        }
    )
    assert response.status_code == 400
    assert "first_name" in response.json()["detail"]
    assert "email" in response.json()["detail"]
    assert "password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_signup_terms_not_accepted(client: AsyncClient):
    response = await client.post(
        "/api/auth/signup",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "password": "securePassword123",
            "terms_accepted": False
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "You must accept the Terms of Use and Privacy Policy"
