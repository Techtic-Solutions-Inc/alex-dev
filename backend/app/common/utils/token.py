"""Token utility functions."""

from app.core.security import create_access_token


def generate_token(user_id: str) -> str:
    """Generate an access token for a validated user identifier."""
    return create_access_token(user_id)
