
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.api.models.user import User


@pytest.fixture
def mock_sendgrid(mocker):
    """Mock SendGrid email sending function."""
    return mocker.patch('src.api.services.email_service.send_verification_email', return_value=None)


def test_email_verification_valid_request(client: TestClient, db_session, mock_sendgrid):
    """Test email verification with a valid request."""
    user = User(
        username="newuser",
        first_name="New",
        last_name="User",
        email="newuser@example.com",
        password_hash="hashedpassword",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/email/verify",
        json={"email": "newuser@example.com", "terms_accepted": True}
    )
    assert response.status_code == 201
    assert response.json()["success"] is True
    mock_sendgrid.assert_called_once()


def test_email_verification_invalid_email_format(client: TestClient):
    """Test email verification with an invalid email format."""
    response = client.post(
        "/api/email/verify",
        json={"email": "invalid-email", "terms_accepted": True}
    )
    assert response.status_code == 400
    assert "Invalid email format" in response.json()["detail"]


def test_email_verification_duplicate_email(client: TestClient, db_session):
    """Test email verification with a duplicate email."""
    user = User(
        username="duplicateuser",
        first_name="Duplicate",
        last_name="User",
        email="duplicate@example.com",
        password_hash="hashedpassword",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/email/verify",
        json={"email": "duplicate@example.com", "terms_accepted": True}
    )
    assert response.status_code == 409
    assert "Email already in use" in response.json()["detail"]


def test_email_verification_terms_not_accepted(client: TestClient):
    """Test email verification without accepting terms of service."""
    response = client.post(
        "/api/email/verify",
        json={"email": "newuser@example.com", "terms_accepted": False}
    )
    assert response.status_code == 400
    assert "Terms must be accepted" in response.json()["detail"]
