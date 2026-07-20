from src.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(user_data):
    """
    Create a new user in the database.
    """
    if User.query.filter_by(email=user_data.email).first():
        raise ValueError("Email already registered")
    hashed_password = pwd_context.hash(user_data.password)
    new_user = User(email=user_data.email, password=hashed_password)
    # Assuming a session object is available
    session.add(new_user)
    session.commit()
    return new_user