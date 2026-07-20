import re
from sqlalchemy.orm import Session
from src.models.user import User


def validate_reset_token(db: Session, token: str) -> None:
    """
    Validate the reset token by checking its format and existence in the database.

    :param db: Database session
    :param token: Password reset token
    :raises ValueError: If the token is invalid or expired
    """
    # Validate token format
    if not re.match(r'^[A-Za-z0-9\-_]+$', token):
        raise ValueError("Invalid token format.")

    # Query the database for the token
    user = db.query(User).filter(User.password_reset_token == token).first()

    if user is None:
        raise ValueError("Invalid or expired reset token.")

    # Additional checks for token expiration can be added here

    # If needed, update the user or token status in the database
    # db.commit()
