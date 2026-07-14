from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.api.v1.models.user import User
from src.api.v1.schemas.auth import LoginRequest, TokenResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    async def login(self, request: LoginRequest) -> TokenResponse:
        user = self.db.query(User).filter(User.email == request.email).first()
        if not user or not self.pwd_context.verify(request.password, user.hashed_password):
            raise ValueError('Invalid credentials')
        # Token generation logic here
        return TokenResponse(access_token='dummy_token')
