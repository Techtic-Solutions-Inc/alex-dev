from fastapi import APIRouter, HTTPException, status, Depends
from src.api.schemas.signup import SignupRequest, SignupResponse
from src.api.services.user_service import create_user_with_confirmation
from src.api.dependencies import get_db

router = APIRouter()

@router.post('/api/auth/signup', response_model=SignupResponse, summary='User signup', description='Register a new user and send confirmation email. This endpoint allows new users to sign up by providing their first name, last name, email, and password. A confirmation email is sent upon successful registration.')
async def signup(request: SignupRequest, db=Depends(get_db)):
    try:
        user_data = await create_user_with_confirmation(request, db)
        return SignupResponse(success=True, message="Signup successful", data=user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signup failed")

@router.post('/api/auth/signup', response_model=SignupResponse, summary='User signup', description='Register a new user and send confirmation email. This endpoint allows new users to sign up by providing their first name, last name, email, and password. A confirmation email is sent upon successful registration.', responses={
    400: {
        "description": "Signup failed due to a bad request.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Signup failed",
                    "error": {"code": "BAD_REQUEST", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Validation error due to incorrect input data.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation Error",
                    "error": {"code": "VALIDATION_ERROR", "details": None},
                }
            }
        },
    },
    500: {
        "description": "Internal server error.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Internal server error.",
                    "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
                }
            }
        },
    },
})
async def signup(request: SignupRequest, db=Depends(get_db)):
    try:
        user_data = await create_user_with_confirmation(request, db)
        return SignupResponse(success=True, message="Signup successful", data=user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Signup failed")
