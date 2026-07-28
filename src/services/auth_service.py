from dataclasses import dataclass

import httpx
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.models import User


class AuthenticationError(Exception):
    """Raised when email/password authentication fails."""


@dataclass(frozen=True)
class AuthSession:
    access_token: str
    token_type: str
    expires_in: int
    redirect_url: str
    user_id: str


class AuthService:
    def __init__(self, settings: Settings | None = None, http_client: httpx.Client | None = None) -> None:
        self._settings = settings or get_settings()
        self._http_client = http_client

    def authenticate_user(self, db: Session, email: str, password: str) -> AuthSession:
        normalized_email = email.strip().lower()
        self._validate_credentials(normalized_email, password)

        token_payload = self._authenticate_with_auth0(normalized_email, password)
        user = self._get_or_create_user(db, normalized_email, token_payload.get("sub"))

        return AuthSession(
            access_token=token_payload["access_token"],
            token_type=token_payload.get("token_type", "Bearer"),
            expires_in=int(token_payload.get("expires_in", 0)),
            redirect_url=self._settings.dashboard_url,
            user_id=str(user.id),
        )

    def _validate_credentials(self, email: str, password: str) -> None:
        if not email:
            raise AuthenticationError("Email is required.")
        if not password:
            raise AuthenticationError("Password is required.")

    def _authenticate_with_auth0(self, email: str, password: str) -> dict[str, object]:
        token_url = self._settings.resolved_auth0_token_url
        if not token_url:
            raise AuthenticationError("Authentication service is not configured.")

        payload = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "client_id": self._settings.auth0_client_id,
            "client_secret": self._settings.auth0_client_secret,
            "audience": self._settings.auth0_audience,
            "scope": "openid profile email",
            "connection": self._settings.auth0_connection,
        }

        try:
            response = self._post_token_request(token_url, payload)
        except httpx.HTTPError as exc:
            raise AuthenticationError("Unable to authenticate at this time.") from exc

        if response.status_code != 200:
            error_description = self._extract_auth0_error(response)
            raise AuthenticationError(error_description)

        data = response.json()
        if "access_token" not in data:
            raise AuthenticationError("Invalid authentication response.")

        return data

    def _post_token_request(self, token_url: str, payload: dict[str, str]) -> httpx.Response:
        if self._http_client is not None:
            return self._http_client.post(token_url, json=payload)

        with httpx.Client(timeout=10.0) as client:
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
        user = db.query(User).filter(User.email == email).one_or_none()
        auth0_subject = str(auth0_id) if auth0_id is not None else None

        if user is None:
            user = User(email=email, auth0_id=auth0_subject, is_active=True)
            db.add(user)
        elif auth0_subject and user.auth0_id != auth0_subject:
            user.auth0_id = auth0_subject

        db.commit()
        db.refresh(user)
        return user


def get_auth_service() -> AuthService:
    return AuthService()
