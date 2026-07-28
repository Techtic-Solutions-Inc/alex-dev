from typing import Any

from auth0.authentication import GetToken
from auth0.authentication.exceptions import Auth0Error

from src.config import Settings, get_settings


class AuthenticationError(Exception):
    """Raised when Auth0 rejects user credentials."""

    def __init__(self, message: str = "Invalid email or password") -> None:
        self.message = message
        super().__init__(message)


class Auth0Service:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def authenticate(self, email: str, password: str) -> dict[str, Any]:
        if not self._settings.auth0_domain:
            raise AuthenticationError("Authentication service is not configured")

        get_token = GetToken(
            self._settings.auth0_domain,
            self._settings.auth0_client_id,
            client_secret=self._settings.auth0_client_secret,
        )

        login_kwargs: dict[str, Any] = {
            "username": email,
            "password": password,
            "realm": self._settings.auth0_connection,
            "scope": "openid profile email",
        }
        if self._settings.auth0_audience:
            login_kwargs["audience"] = self._settings.auth0_audience

        try:
            return get_token.login(**login_kwargs)
        except Auth0Error as exc:
            raise AuthenticationError(self._map_auth0_error(exc)) from exc

    @staticmethod
    def _map_auth0_error(error: Auth0Error) -> str:
        error_code = getattr(error, "error_code", None) or getattr(error, "status_code", None)
        message = str(error.message) if hasattr(error, "message") else str(error)

        if error_code == "invalid_grant" or "Wrong email or password" in message:
            return "Invalid email or password"
        if error_code == "too_many_attempts":
            return "Too many failed login attempts. Please try again later."
        if error_code == "access_denied":
            return "Access denied. Please check your credentials."
        return "Invalid email or password"
