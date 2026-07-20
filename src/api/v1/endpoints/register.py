import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.v1.controllers.auth_controller import AuthController
from src.api.v1.models.auth import RegisterRequest, RegisterResponse
from src.db.session import get_db

logger = logging.getLogger(__name__)
router = APIRouter()
auth_controller = AuthController()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    return auth_controller.register(payload, db)
