"""Input validation helpers for authentication flows."""

import re

from email_validator import EmailNotValidError, validate_email

PASSWORD_MIN_LENGTH = 8
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$"
)


def normalize_email(email: str) -> str:
    """Normalize and validate an email address."""
    normalized = email.strip().lower()
    try:
        result = validate_email(normalized, check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError("Invalid email format.") from exc
    return result.normalized


def is_valid_email(email: str) -> bool:
    """Return True when the email address has a valid format."""
    try:
        normalize_email(email)
    except ValueError:
        return False
    return True


def validate_password_strength(password: str) -> None:
    """Raise ValueError when the password does not meet strength requirements."""
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(
            "Password must be at least 8 characters long and include an uppercase "
            "letter, a number, and a special character."
        )
    if not PASSWORD_PATTERN.match(password):
        raise ValueError(
            "Password must be at least 8 characters long and include an uppercase "
            "letter, a number, and a special character."
        )
