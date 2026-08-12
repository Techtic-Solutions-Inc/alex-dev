
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signin_invalid_email_format(client: AsyncClient):
    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "invalid-email",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid email format"


@pytest.mark.asyncio
async def test_signin_incorrect_credentials(client: AsyncClient):
    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_signin_success(client: AsyncClient, db_session):
    # Pre-insert a user
    db_session.execute(
        """
        INSERT INTO users (username, email, first_name, last_name, hashed_password, is_locked)
        VALUES ('johndoe', 'john.doe@example.com', 'John', 'Doe', 'hashedpassword', false)
        """
    )
    db_session.commit()

    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "john.doe@example.com",
            "password": "securePassword123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_signin_empty_fields(client: AsyncClient):
    response = await client.post(
        "/api/auth/signin",
        json={
            "email": "",
            "password": ""
        }
    )
    assert response.status_code == 400
    assert "email" in response.json()["detail"]
    assert "password" in response.json()["detail"]
