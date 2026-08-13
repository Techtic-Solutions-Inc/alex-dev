from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

class SignupRequest(BaseModel):
    first_name: str = Field(..., description="User's first name", example="John")
    last_name: str = Field(..., description="User's last name", example="Doe")
    email: str = Field(..., description="User's email address", example="john.doe@example.com")
    password: str = Field(..., description="User's password", example="strongpassword123")

class SignupResponse(BaseModel):
    message: str = Field(..., description="Success message", example="User registered successfully")

router = APIRouter()

@router.post("/signup", response_model=SignupResponse, summary="Register a new user", description="Register a new user with first name, last name, email, and password.")
async def signup(body: SignupRequest):
    # Implementation here
    return {"message": "User registered successfully"}
