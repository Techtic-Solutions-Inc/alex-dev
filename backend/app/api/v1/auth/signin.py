from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

class SigninRequest(BaseModel):
    email: str = Field(..., description="User's email address", example="john.doe@example.com")
    password: str = Field(..., description="User's password", example="strongpassword123")

class SigninResponse(BaseModel):
    token: str = Field(..., description="JWT token for authentication", example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

router = APIRouter()

@router.post("/signin", response_model=SigninResponse, summary="Authenticate user and return token", description="Authenticate user using email and password and return a JWT token.")
async def signin(body: SigninRequest):
    # Implementation here
    return {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
