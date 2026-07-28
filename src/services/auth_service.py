from typing import Any

from auth0.authentication import GetToken
from auth0.exceptions import Auth0Error

from src.config.settings import (
    AUTH0_CLIENT_ID,
    AUTH0_CLIENT_SECRET,
    AUTH0_CONNECTION,
    AUTH0_DOMAIN,
)
from src.utils.logger import logger


class AuthenticationError(Exception):
    """Raised when user credentials are invalid or authentication fails."""


def authenticate_with_auth0(email: str, password: str) -> dict[str, Any]:
    """Validate user credentials against Auth0 and return token data."""
    if not AUTH0_DOMAIN or not AUTH0_CLIENT_ID:
        logger.error("Auth0 configuration is incomplete")
        raise AuthenticationError("Authentication service is unavailable")

    try:
        get_token = GetToken(
            AUTH0_DOMAIN,
            AUTH0_CLIENT_ID,
            client_secret=AUTH0_CLIENT_SECRET or None,
        )
        token_response = get_token.login(
            username=email,
            password=password,
            realm=AUTH0_CONNECTION,
            scope="openid profile email",
        )
        logger.info("Successful authentication for email=%s", email)
        return token_response
    except Auth0Error as exc:
        logger.warning("Failed authentication for email=%s: %s", email, exc)
        raise AuthenticationError("Invalid credentials") from exc
