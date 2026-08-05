import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from utils.password import hash_password

STRONG_PASSWORD = "StrongPass1!"


@pytest.mark.asyncio
async def test_get_users_summary_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    db_session.add_all(
        [
            User(
                email="active1@example.com",
                hashed_password=hash_password(STRONG_PASSWORD),
                is_active=True,
            ),
            User(
                email="active2@example.com",
                hashed_password=hash_password(STRONG_PASSWORD),
                is_active=True,
            ),
            User(
                email="inactive@example.com",
                hashed_password=hash_password(STRONG_PASSWORD),
                is_active=False,
            ),
        ]
    )
    await db_session.commit()

    response = await client.get("/api/users/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 3
    assert data["active_users"] == 2


@pytest.mark.asyncio
async def test_get_users_summary_no_users(client: AsyncClient) -> None:
    response = await client.get("/api/users/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_users"] == 0
    assert data["active_users"] == 0
