from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()

class LoginRequest(BaseModel):
    username: str = Field(..., description='The username of the user', example='johndoe')
    password: str = Field(..., description='The password of the user', example='secret')

class LoginResponse(BaseModel):
    access_token: str = Field(..., description='JWT access token', example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
    token_type: str = Field(..., description='Type of the token', example='bearer')

@router.post('/auth/login', summary='Authenticate user', description='Authenticates a user and returns a JWT token.', response_model=LoginResponse)
async def login(body: LoginRequest):
    # Authentication logic here
    if body.username != 'johndoe' or body.password != 'secret':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...', 'token_type': 'bearer'}
