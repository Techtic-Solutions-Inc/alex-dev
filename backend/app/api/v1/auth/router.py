from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.exceptions.http_exceptions import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

router = APIRouter()

auth_service = AuthService()

@router.post('/signup', response_model=UserResponse, status_code=201, summary='Register a new user', description='Create a new user account with email and password. Returns the created user details.')
async def signup(user_create: UserCreate):
    """
    Register a new user.

    - **email**: Email of the user
    - **password**: Password for the account
    """
    user = await auth_service.create_user(user_create)
    if not user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='User already exists')
    return user

@router.post('/signin', response_model=Token, summary='Authenticate user and return token', description='Authenticate an existing user and return a JWT token for session management.')
async def signin(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return token.

    - **username**: Email of the user
    - **password**: Password for the account
    """
    token = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    return token
