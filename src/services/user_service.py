import sqlalchemy as sa
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str):
        # Use parameterized query to prevent SQL injection
        query = sa.text("SELECT * FROM users WHERE email = :email")
        result = self.db.execute(query, {'email': email})
        return result.fetchone()

    def authenticate_user(self, db: Session, email: str, password: str):
        user = self.get_user_by_email(email)
        if not user:
            raise AuthenticationError("user_not_found", "User not found")

        # Assume some password verification logic here
        if not self.verify_password(password, user.password):
            raise AuthenticationError("invalid_credentials", "Invalid credentials")

        # Assume session creation logic here
        return self.create_session(user)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        # Placeholder for password verification logic
        return plain_password == hashed_password

    def create_session(self, user):
        # Placeholder for session creation logic
        return {
            'access_token': 'dummy_access_token',
            'token_type': 'bearer',
            'expires_in': 3600,
            'redirect_url': '/dashboard',
            'email': user.email
        }

class AuthenticationError(Exception):
    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message

# Dependency

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)