from src.config.settings import settings
from tests.conftest import EXPIRED_RESET_TOKEN, VALID_RESET_TOKEN


def test_reset_password_success(client, user_with_valid_reset_token):
    response = client.post(
        "/reset-password",
        json={
            "token": VALID_RESET_TOKEN,
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
    )

    assert response.status_code == 200
    assert (
        response.json()["message"]
        == "Your password has been reset successfully! You can now log in."
    )


def test_reset_password_invalid_token(client, db_session):
    response = client.post(
        "/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired reset link"


def test_reset_password_mismatched_passwords(client, user_with_valid_reset_token):
    response = client.post(
        "/reset-password",
        json={
            "token": VALID_RESET_TOKEN,
            "new_password": "NewPassword123!",
            "confirm_password": "DifferentPassword123!",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match"


def test_reset_password_link_redirects_to_page(client, user_with_valid_reset_token):
    response = client.get(
        f"/reset-password?token={VALID_RESET_TOKEN}",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["location"] == (
        f"{settings.PASSWORD_RESET_FRONTEND_URL}?token={VALID_RESET_TOKEN}"
    )


def test_reset_password_link_invalid_token(client, db_session):
    response = client.get(
        "/reset-password?token=invalid-token",
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired reset link"


def test_reset_password_link_expired_token(client, user_with_expired_reset_token):
    response = client.get(
        f"/reset-password?token={EXPIRED_RESET_TOKEN}",
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired reset link"
