from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth_service import login_user
from src.config.database import get_db
from src.middlewares.auth import get_current_user_record

router = APIRouter()

@router.post(
    "/login",
    summary="Authenticate user and return token",
    description="Authenticate a user using email and password, returning a JWT token if successful.",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "User authenticated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Invalid email or password.",
                        "error": {"code": "INVALID_CREDENTIALS", "details": None}
                    }
                }
            }
        },
        500: {
            "description": "Unexpected server error.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal Server Error",
                        "success": False,
                        "message": "Internal Server Error",
                        "error": {"code": "INTERNAL_SERVER_ERROR", "details": None}
                    }
                }
            }
        }
    },
    tags=["Authentication"]
)
async def login(
    email: str, password: str, db: Session = Depends(get_db)
) -> LoginResponse:
    """Authenticate user and return JWT token."""
    return await login_user(email, password, db)
