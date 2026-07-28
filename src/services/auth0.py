from typing import Any

import httpx

from src.config import Settings


class Auth0AuthenticationError(Exception):
    def __init__(self, message: str, error_code: str = "invalid_credentials") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class Auth0Service:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def _token_url(self) -> str:
        return f"https://{self._settings.auth0_domain}/oauth/token"

    async def authenticate(self, email: str, password: str) -> dict[str, Any]:
        if not self._settings.auth0_domain or not self._settings.auth0_client_id:
            raise Auth0AuthenticationError(
                "Authentication service is not configured",
                error_code="service_unavailable",
            )

        payload = {
            "grant_type": "http://auth0.com/oauth/grant-type/password-realm",
            "username": email,
            "password": password,
            "client_id": self._settings.auth0_client_id,
            "client_secret": self._settings.auth0_client_secret,
            "realm": self._settings.auth0_connection,
            "scope": "openid profile email",
        }
        if self._settings.auth0_audience:
            payload["audience"] = self._settings.auth0_audience

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self._token_url, json=payload)

        if response.status_code == 200:
            return response.json()

        error_body = response.json() if response.content else {}
        error_description = error_body.get("error_description", "Invalid email or password")
        raise Auth0AuthenticationError(error_description)
