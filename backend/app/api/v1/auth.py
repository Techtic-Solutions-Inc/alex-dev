
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()

class SignupRequest(BaseModel):
    first_name: str = Field(..., description="User's first name", example="John")
    last_name: str = Field(..., description="User's last name", example="Doe")
    email: EmailStr = Field(..., description="User's email address", example="john.doe@example.com")
    password: str = Field(..., description="User's password", example="strongpassword123")
    terms_accepted: bool = Field(..., description="User has accepted terms and conditions", example=True)

class SignupResponse(BaseModel):
    user_id: int = Field(..., description="Unique identifier for the user", example=123)
    message: str = Field(..., description="Success message", example="User registered successfully")

class ErrorResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the request was successful", example=False)
    message: str = Field(..., description="Error message", example="Invalid input")
    error_code: int = Field(..., description="Specific error code", example=400)

@router.post("/auth/signup", response_model=SignupResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    409: {"model": ErrorResponse, "description": "Conflict"}
})
async def signup(body: SignupRequest):
    """
    Register a new user.

    This endpoint allows a new user to register by providing their first name, last name, email, password, and acceptance of terms.
    """
    # Implementation goes here
    pass

class SigninRequest(BaseModel):
    email: EmailStr = Field(..., description="User's email address", example="john.doe@example.com")
    password: str = Field(..., description="User's password", example="strongpassword123")

class SigninResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(..., description="Type of the token", example="bearer")

@router.post("/auth/signin", response_model=SigninResponse, responses={
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    422: {"model": ErrorResponse, "description": "Unprocessable Entity"}
})
async def signin(body: SigninRequest):
    """
    Authenticate a user.

    This endpoint allows a user to authenticate by providing their email and password.
    """
    # Implementation goes here
    pass
