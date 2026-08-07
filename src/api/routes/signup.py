```python
from fastapi import APIRouter, HTTPException, status
from src.api.schemas.signup import SignupRequest, SignupResponse
from src.api.services.user_service import create_user_with_confirmation
from loguru import logger

router = APIRouter()

@router.post(
    "/api/auth/signup",
    response_model=SignupResponse,
    summary="User signup",
    description="Register a new user and send confirmation email. "
                "The user must provide a valid email, password, first name, and last name. "
                "A confirmation email will be sent to the provided email address. "
                "Returns HTTP 400 if any required field is missing or invalid.",
    responses={
        200: {
            "description": "Signup successful.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Signup successful",
                        "data": {"user_id": "new_user_id"},
                    }
                }
            },
        },
        400: {
            "description": "Invalid input.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Invalid input data.",
                        "error": {"code": "INVALID_INPUT", "details": "Email, password, first name, and last name are required."},
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
)
async def signup(request: SignupRequest):
    """Register a new user and send confirmation email."""
    try:
        user_id = await create_user_with_confirmation(request)
        return SignupResponse(success=True, message="Signup successful", data={"user_id": user_id})
    except ValueError as e:
        logger.error(f"Signup failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```