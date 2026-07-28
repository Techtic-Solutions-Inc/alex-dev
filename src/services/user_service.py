from dataclasses import dataclass
import logging

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.models import User

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    def __init__(self, message: str, error_code: str = "invalid_credentials") -> None:
        self.message = message
        self.error_code = error_code
        super().__init__(message)


@dataclass(frozen=True)
class AuthSession:
    access_token: str
    token_type: str
    expires_in: int
    redirect_url: str
    email: str
    user_id: str


class UserService:
    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._http_client = http_client

    def authenticate_user(self, db: Session, email: str, password: str) -> AuthSession:
        normalized_email = email.strip().lower()
        self._validate_credentials(normalized_email, password)

        token_payload = self._authenticate_with_auth0(normalized_email, password)
        user = self._get_or_create_user(db, normalized_email, token_payload.get("sub"))

        logger.info("User authenticated successfully: %s", normalized_email)

        return AuthSession(
            access_token=str(token_payload["access_token"]),
            token_type=str(token_payload.get("token_type", "Bearer")),
            expires_in=int(token_payload.get("expires_in", 86400)),
            redirect_url=self._settings.dashboard_redirect_url,
            email=normalized_email,
            user_id=str(user.id),
        )

    def _validate_credentials(self, email: str, password: str) -> None:
        if not email:
            raise AuthenticationError("Email is required.", error_code="validation_error")
        if not password:
            raise AuthenticationError("Password is required.", error_code="validation_error")

    def _authenticate_with_auth0(self, email: str, password: str) -> dict[str, object]:
        if not self._settings.auth0_domain or not self._settings.auth0_client_id:
            logger.error("Auth0 configuration is missing")
            raise AuthenticationError(
                "Authentication service is not configured.",
                error_code="service_unavailable",
            )

        payload: dict[str, str] = {
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

        try:
            response = self._post_token_request(self._settings.auth0_token_url, payload)
        except httpx.HTTPError as exc:
            logger.exception("Auth0 request failed")
            raise AuthenticationError(
                "Unable to authenticate at this time.",
                error_code="service_unavailable",
            ) from exc

        if response.status_code != 200:
            error_message = self._extract_auth0_error(response)
            logger.warning("Auth0 authentication failed for %s: %s", email, error_message)
            raise AuthenticationError(error_message)

        data = response.json()
        if "access_token" not in data:
            raise AuthenticationError("Invalid authentication response.")

        return data

    def _post_token_request(self, token_url: str, payload: dict[str, str]) -> httpx.Response:
        if self._http_client is not None:
            return self._http_client.post(token_url, json=payload)

        with httpx.Client(timeout=30.0) as client:
            return client.post(token_url, json=payload)

    def _extract_auth0_error(self, response: httpx.Response) -> str:
        try:
            body = response.json()
        except ValueError:
            return "Invalid email or password."

        error_description = body.get("error_description") or body.get("error")
        if isinstance(error_description, str) and error_description:
            if "wrong email or password" in error_description.lower():
                return "Invalid email or password."
            return error_description

        return "Invalid email or password."

    def _get_or_create_user(self, db: Session, email: str, auth0_id: object | None) -> User:
        stmt = select(User).where(User.email == email)
        user = db.scalars(stmt).one_or_none()
        auth0_subject = str(auth0_id) if auth0_id is not None else None

        if user is None:
            user = User(email=email, auth0_id=auth0_subject, is_active=True)
            db.add(user)
        elif auth0_subject and user.auth0_id != auth0_subject:
            user.auth0_id = auth0_subject

        db.commit()
        db.refresh(user)
        return user


def get_user_service() -> UserService:
    return UserService()
