from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.models.user import User
from src.schemas.auth import LoginRequest, TokenResponse
from src.utils.jwt import create_access_token
from src.utils.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def login_user(db: Session, request: LoginRequest) -> TokenResponse:
    user = authenticate_user(db, request.email, request.password)
    if not user:
        logger.warning("Failed login attempt for email=%s", request.email)
        raise ValueError("Invalid credentials")

    access_token = create_access_token(str(user.id), {"email": user.email})
    logger.info("Successful login for user_id=%s email=%s", user.id, user.email)
    return TokenResponse(access_token=access_token)
