"""JWT authentication middleware."""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.utils.token import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Retrieve the current authenticated user ID from the JWT token."""
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
            )
        return user_id
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        ) from exc
