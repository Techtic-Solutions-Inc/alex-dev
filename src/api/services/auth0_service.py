"""Auth0 authentication integration."""

from __future__ import annotations

import httpx
from loguru import logger

from src.config.settings import Settings, get_settings
from src.exceptions import ConflictError, UnauthorizedError

__all__ = ["Auth0AuthenticationService", "get_auth0_service"]


class Auth0AuthenticationService:
    """Authenticate users against Auth0 when configured."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def is_enabled(self) -> bool:
        """Return True when all required Auth0 settings are present."""
        return bool(
            self._settings.auth0_domain
            and self._settings.auth0_client_id
            and self._settings.auth0_client_secret
        )

    def authenticate(self, email: str, password: str) -> dict:
        """Validate credentials with Auth0 and return the token response."""
        if not self.is_enabled:
            raise RuntimeError("Auth0 is not configured")

        token_url = f"https://{self._settings.auth0_domain}/oauth/token"
        payload: dict[str, str] = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "client_id": self._settings.auth0_client_id,
            "client_secret": self._settings.auth0_client_secret,
            "scope": "openid profile email",
        }
        if self._settings.auth0_audience:
            payload["audience"] = self._settings.auth0_audience

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(token_url, json=payload)
        except httpx.HTTPError as exc:
            logger.error("Auth0 authentication request failed: {}", exc)
            raise UnauthorizedError(
                message="Authentication service is temporarily unavailable.",
                code="AUTHENTICATION_SERVICE_ERROR",
            ) from exc

        if response.status_code == 200:
            return response.json()

        logger.warning(
            "Auth0 rejected credentials for {} with status {}",
            email,
            response.status_code,
        )
        raise ConflictError(
            message="Incorrect email or password.",
            code="INCORRECT_PASSWORD",
        )

    def verify_webhook_signature(
        self,
        payload: bytes,
        signature: str | None,
    ) -> bool:
        """Verify an Auth0 webhook signature when a secret is configured."""
        secret = self._settings.auth0_webhook_secret
        if not secret:
            return True
        if not signature:
            return False

        import hashlib
        import hmac

        expected = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)


def get_auth0_service(settings: Settings | None = None) -> Auth0AuthenticationService:
    """Return an Auth0 authentication service instance."""
    return Auth0AuthenticationService(settings)
