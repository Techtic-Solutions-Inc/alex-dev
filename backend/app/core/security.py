import jwt
from typing import Any, Dict

from app.core.config import settings

ALGORITHM = "HS256"
PASSWORD_RESET_TOKEN_TYPE = "password_reset"


def verify_token(token: str) -> Dict[str, Any]:
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
    if payload.get("type") == PASSWORD_RESET_TOKEN_TYPE:
        raise ValueError("Invalid or expired token")
    return payload


def get_current_user(token: str) -> Dict[str, Any]:
    try:
        payload = verify_token(token)
        # Additional logic to retrieve user from payload
    except ValueError as e:
        raise Exception("Authentication failed") from e
    return payload