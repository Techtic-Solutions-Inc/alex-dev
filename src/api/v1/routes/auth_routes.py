from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.v1.controllers.auth_controller import AuthController
from src.api.v1.models.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    UserOut,
)
from src.db.session import get_db
from src.middlewares.auth import get_current_user
from src.models.user import User

router = APIRouter()
auth_controller = AuthController()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    return auth_controller.login(payload, db)


@router.post(
    "/auth/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    return auth_controller.register(payload, db)


@router.get("/users/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)
