import base64
import json
from typing import Any

from sqlalchemy import bindparam, select
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.models.user import User
from src.schemas.auth import AuthenticatedUserResponse, AuthenticateResponse
from src.services.auth0_service import Auth0Service, AuthenticationError


class UserService:
    def __init__(
        self,
        db: Session,
        auth0_service: Auth0Service | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._db = db
        self._auth0_service = auth0_service or Auth0Service(settings=settings)
        self._settings = settings or get_settings()

    def authenticate(self, email: str, password: str) -> AuthenticateResponse:
        normalized_email = email.strip().lower()
        token_data = self._auth0_service.authenticate(normalized_email, password)
        user = self._get_or_create_user(normalized_email, token_data)
        return self._build_response(token_data, user)

    def _get_or_create_user(self, email: str, token_data: dict[str, Any]) -> User:
        stmt = select(User).where(User.email == bindparam("email"))
        user = self._db.scalars(stmt, {"email": email}).one_or_none()
        auth0_id = self._extract_auth0_id(token_data)

        if user is None:
            user = User(email=email, auth0_id=auth0_id)
            self._db.add(user)
        elif auth0_id and user.auth0_id != auth0_id:
            user.auth0_id = auth0_id

        self._db.commit()
        self._db.refresh(user)
        return user

    def _build_response(self, token_data: dict[str, Any], user: User) -> AuthenticateResponse:
        return AuthenticateResponse(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=int(token_data.get("expires_in", 0)),
            redirect_url=self._settings.dashboard_url,
            user=AuthenticatedUserResponse(
                id=str(user.id),
                email=user.email,
            ),
        )

    @staticmethod
    def _extract_auth0_id(token_data: dict[str, Any]) -> str | None:
        id_token = token_data.get("id_token")
        if not id_token:
            return None

        try:
            payload_segment = id_token.split(".")[1]
            padding = "=" * (-len(payload_segment) % 4)
            decoded_payload = base64.urlsafe_b64decode(payload_segment + padding)
            return json.loads(decoded_payload).get("sub")
        except (IndexError, ValueError, json.JSONDecodeError):
            return None


__all__ = ["AuthenticationError", "UserService"]
