from sqlalchemy.orm import Session
from src.models.user import User

class AuthService:
    def _get_or_create_user(self, db: Session, email: str) -> User:
        # Use ORM filtering to prevent SQL injection
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    # Other methods of AuthService
