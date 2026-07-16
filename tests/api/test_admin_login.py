import jwt
from src.config.settings import JWT_SECRET, JWT_ALGORITHM


def test_admin_login_success(client, sample_admin):
    response = client.post(
        "/api/v1/admin/login",
        json={"email": "admin@example.com", "password": "adminpassword"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    payload = jwt.decode(body["access_token"], JWT_SECRET, algorithms=[JWT_ALGORITHM])
    assert payload["sub"] == str(sample_admin.id)
    assert payload["email"] == sample_admin.email
    assert payload["role"] == "admin"


def test_admin_login_invalid_credentials(client, sample_admin):
    response = client.post(
        "/api/v1/admin/login",
        json={"email": "admin@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_admin_login_logging(client, sample_admin, caplog):
    import logging

    with caplog.at_level(logging.INFO):
        client.post(
            "/api/v1/admin/login",
            json={"email": "admin@example.com", "password": "adminpassword"},
        )

    assert any(
        "Admin login attempt for email=admin@example.com" in record.message
        for record in caplog.records
    )
    assert any(
        "Successful admin login for admin_id=" in record.message
        for record in caplog.records
    )

    with caplog.at_level(logging.WARNING):
        client.post(
            "/api/v1/admin/login",
            json={"email": "admin@example.com", "password": "wrongpassword"},
        )

    assert any(
        "Failed admin login attempt for email=admin@example.com" in record.message
        for record in caplog.records
    )
