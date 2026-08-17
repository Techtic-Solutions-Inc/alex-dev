"""Shared helpers for API tests."""


def signup_payload(**overrides: object) -> dict[str, object]:
    """Return a valid signup payload with optional field overrides."""
    payload: dict[str, object] = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "StrongPassword123!",
        "terms_accepted": True,
    }
    payload.update(overrides)
    return payload
