from sqlalchemy.orm import Session

from src.models.user import User
from src.utils.email import send_confirmation_email
from src.utils.security import create_access_token, hash_password, verify_password

DUPLICATE_EMAIL_MESSAGE = "Email already in use. Please use a different email address."


class AuthService:
    """Business logic for authentication workflows."""

    def authenticate_user(
        self, db: Session, email: str, password: str
    ) -> User | None:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_token_for_user(self, user: User) -> str:
        return create_access_token(data={"sub": str(user.id), "email": user.email})

    def register_user(self, db: Session, email: str, password: str) -> User:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError(DUPLICATE_EMAIL_MESSAGE)

        user = User(
            email=email,
            hashed_password=hash_password(password),
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        try:
            send_confirmation_email(user.email)
        except Exception as exc:
            raise RuntimeError("Confirmation email delivery failed") from exc

        return user

    def get_user_by_id(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()
