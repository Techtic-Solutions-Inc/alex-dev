from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class PasswordResetRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class PasswordResetResponse(BaseModel):
    message: str

@app.post("/reset-password", response_model=PasswordResetResponse, responses={400: {"description": "Bad Request"}, 401: {"description": "Unauthorized"}})
async def reset_password(request: PasswordResetRequest):
    """
    summary: Reset user password
    description: This endpoint allows users to reset their password using a valid reset token.
    """
    # Implementation goes here
    pass