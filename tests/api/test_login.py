import jwt
from src.config.settings import JWT_SECRET, JWT_ALGORITHM


def test_login_success(client, sample_user):
    response = client.post(
        "/api/v1/login",
        json={"email": "testuser@example.com", "password": "securepassword"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    payload = jwt.decode(body["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == str(sample_user.id)
    assert payload["email"] == sample_user.email


def test_login_invalid_credentials(client, sample_user):
    response = client.post(
        "/api/v1/login",
        json={"email": "testuser@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_logging(client, sample_user, caplog):
    import logging

    with caplog.at_level(logging.INFO):
        client.post(
            "/api/v1/login",
            json={"email": "testuser@example.com", "password": "securepassword"},
        )

    assert any("Login attempt for email=testuser@example.com" in record.message for record in caplog.records)
    assert any("Successful login for user_id=" in record.message for record in caplog.records)

    with caplog.at_level(logging.WARNING):
        client.post(
            "/api/v1/login",
            json={"email": "testuser@example.com", "password": "wrongpassword"},
        )

    assert any("Failed login attempt for email=testuser@example.com" in record.message for record in caplog.records)
