import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.v1.controllers.auth_controller import AuthController
from src.api.v1.models.auth import LoginRequest, LoginResponse
from src.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter()
auth_controller = AuthController()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    return auth_controller.login(payload, db)
