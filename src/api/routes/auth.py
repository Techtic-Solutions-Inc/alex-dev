"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.services.auth_service import authenticate_user
from src.config.database import get_db
from src.config.settings import get_settings
from src.schemas.auth import LoginRequest, LoginResponse
from src.utils.token import generate_access_token

settings = get_settings()
router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description=(
        "Authenticate a user and return a JWT access token. Requires valid "
        "username and password."
    ),
    responses={
        200: {
            "description": "Successful login returns an access token.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid username or password"},
                }
            },
        },
        422: {
            "description": "Validation error.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation Error",
                        "error": {"code": "VALIDATION_ERROR", "details": None},
                        "detail": "Validation Error",
                        "errors": [
                            {"field": "username", "message": "Field required"}
                        ],
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal Server Error",
                        "success": False,
                        "message": "Internal Server Error",
                        "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
                    }
                }
            },
        },
    },
    tags=["Authentication"],
    dependencies=[Depends(get_db)],
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> dict[str, str | int]:
    """Authenticate credentials and issue a JWT access token."""
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = generate_access_token(
        {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.effective_jwt_expiry,
    }
