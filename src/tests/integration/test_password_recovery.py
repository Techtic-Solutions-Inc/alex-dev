
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.api.models.user import User
from src.config.settings import get_settings


@pytest.fixture
def mock_sendgrid(mocker):
    """Mock SendGrid email sending function."""
    return mocker.patch('src.api.services.email_service.send_password_reset_email', return_value=None)


def test_password_recovery_valid_email(client: TestClient, db_session, mock_sendgrid):
    """Test password recovery with a valid email."""
    user = User(
        username="validuser",
        first_name="Valid",
        last_name="User",
        email="validuser@example.com",
        password_hash="hashedpassword",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/password-recovery",
        json={"email": "validuser@example.com", "terms_accepted": True}
    )
    assert response.status_code == 201
    assert response.json()["success"] is True
    mock_sendgrid.assert_called_once()


def test_password_recovery_invalid_email_format(client: TestClient):
    """Test password recovery with an invalid email format."""
    response = client.post(
        "/api/password-recovery",
        json={"email": "invalid-email", "terms_accepted": True}
    )
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]


def test_password_recovery_non_existent_email(client: TestClient):
    """Test password recovery with a non-existent email."""
    response = client.post(
        "/api/password-recovery",
        json={"email": "nonexistent@example.com", "terms_accepted": True}
    )
    assert response.status_code == 404
    assert "Email not registered" in response.json()["detail"]


def test_password_recovery_empty_email_field(client: TestClient):
    """Test password recovery with an empty email field."""
    response = client.post(
        "/api/password-recovery",
        json={"email": "", "terms_accepted": True}
    )
    assert response.status_code == 400
    assert "Email is required" in response.json()["detail"]


def test_password_recovery_terms_not_accepted(client: TestClient):
    """Test password recovery without accepting terms of service."""
    response = client.post(
        "/api/password-recovery",
        json={"email": "validuser@example.com", "terms_accepted": False}
    )
    assert response.status_code == 400
    assert "Terms must be accepted" in response.json()["detail"]
