from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from src.models.user import User
from src.schemas.auth import AuthenticateRequest, AuthenticateResponse
from src.services.auth0_service import AuthenticationError


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate(self, email: str, password: str) -> AuthenticateResponse:
        # Use parameterized query to prevent SQL injection
        try:
            user = self.db.query(User).filter(User.email == email).one()
        except NoResultFound:
            raise AuthenticationError("Invalid email or password")

        # Assuming a function `verify_password` exists to check the password
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        # Assuming a function `create_access_token` exists to create a token
        access_token = create_access_token(data={"sub": user.email})

        return AuthenticateResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,  # Example expiration time
            redirect_url="/dashboard",
            user=AuthenticatedUserResponse(id=str(user.id), email=user.email)
        )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Placeholder for password verification logic
    return True


def create_access_token(data: dict) -> str:
    # Placeholder for token creation logic
    return "token"