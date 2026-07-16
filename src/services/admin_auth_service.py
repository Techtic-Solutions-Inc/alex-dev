from sqlalchemy.orm import Session

from src.models.admin import Admin
from src.schemas.auth import LoginRequest, TokenResponse
from src.services.auth_service import verify_password
from src.utils.jwt import create_access_token
from src.utils.logger import logger


def authenticate_admin(db: Session, email: str, password: str) -> Admin | None:
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not verify_password(password, admin.hashed_password):
        return None
    return admin


def login_admin(db: Session, request: LoginRequest) -> TokenResponse:
    admin = authenticate_admin(db, request.email, request.password)
    if not admin:
        logger.warning("Failed admin login attempt for email=%s", request.email)
        raise ValueError("Invalid credentials")

    access_token = create_access_token(
        str(admin.id), {"email": admin.email, "role": "admin"}
    )
    logger.info("Successful admin login for admin_id=%s email=%s", admin.id, admin.email)
    return TokenResponse(access_token=access_token)
