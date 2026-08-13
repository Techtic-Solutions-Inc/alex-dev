from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

class PasswordRecoveryRequest(BaseModel):
    email: str = Field(..., description="User's email address for password recovery", example="john.doe@example.com")

class PasswordRecoveryResponse(BaseModel):
    message: str = Field(..., description="Success message", example="Password recovery email sent")

router = APIRouter()

@router.post("/password-recovery", response_model=PasswordRecoveryResponse, summary="Initiate password recovery process", description="Send a password recovery email to the user.")
async def password_recovery(body: PasswordRecoveryRequest):
    # Implementation here
    return {"message": "Password recovery email sent"}
