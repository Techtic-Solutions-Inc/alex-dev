from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.user import User
from src.utils.security import verify_password

STRONG_PASSWORD = "Password1!"


@patch("src.api.v1.services.auth_service.send_confirmation_email")
def test_user_registration_and_login_workflow(
    mock_send_email,
    client: TestClient,
    db_session: Session,
) -> None:
    register_response = client.post(
        "/auth/register",
        json={"email": "workflow@example.com", "password": STRONG_PASSWORD},
    )
    assert register_response.status_code == 201

    user = db_session.query(User).filter(User.email == "workflow@example.com").one()
    assert verify_password(STRONG_PASSWORD, user.hashed_password)
    mock_send_email.assert_called_once_with("workflow@example.com")

    login_response = client.post(
        "/login",
        json={"email": "workflow@example.com", "password": STRONG_PASSWORD},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    profile_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "workflow@example.com"
