import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rate_limiting_middleware(client: AsyncClient, test_users):
    # Test hitting the endpoint within the rate limit
    for _ in range(10):
        response = await client.post(
            "/api/v1/user/authenticate",
            json={"email": "user@test.com", "password": "TestUser123!"}
        )
        assert response.status_code == status.HTTP_200_OK

    # Test exceeding the rate limit
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert response.json()["detail"] == "Rate limit exceeded"


@pytest.mark.asyncio
async def test_rate_limit_configuration(client: AsyncClient, test_users):
    # Ensure configuration allows for rate limiting by IP
    response = await client.post(
        "/api/v1/user/authenticate",
        json={"email": "user@test.com", "password": "TestUser123!"}
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_rate_limit_feedback(client: AsyncClient, test_users):
    # Exceed rate limit to check feedback mechanism
    for _ in range(11):
        response = await client.post(
            "/api/v1/user/authenticate",
            json={"email": "user@test.com", "password": "TestUser123!"}
        )

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Rate limit exceeded" in response.json()["detail"]
