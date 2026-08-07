from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth0_service import Auth0AuthenticationService
from src.config.settings import get_settings
from src.utils.password import hash_password
from src.utils.validation import normalize_email


def create_user_with_confirmation(db: Session, email: str, password: str) -> User:
    """Create a new user with email confirmation and provision in Auth0 if enabled."""
    normalized_email = normalize_email(email)
    password_hash = hash_password(password)

    user = User(email=normalized_email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Provision user in Auth0 if enabled
    settings = get_settings()
    auth0_service = Auth0AuthenticationService(settings)
    if auth0_service.is_enabled:
        auth0_service.create_user(
            email=normalized_email,
            password=password,
            connection='Username-Password-Authentication'
        )

    return user
