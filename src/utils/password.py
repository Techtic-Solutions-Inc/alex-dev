import re

import bcrypt

MIN_PASSWORD_LENGTH = 8

_STRENGTH_RULES: list[tuple[str, str]] = [
    (r"[A-Z]", "at least one uppercase letter"),
    (r"[a-z]", "at least one lowercase letter"),
    (r"\d", "at least one digit"),
    (r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;/'`~]", "at least one special character"),
]


def validate_password_strength(password: str) -> None:
    """Raise ValueError when the password does not meet strength requirements.

    Requirements: minimum 8 characters, at least one uppercase letter, one
    lowercase letter, one digit, and one special character.
    """
    failures: list[str] = []

    if len(password) < MIN_PASSWORD_LENGTH:
        failures.append(f"at least {MIN_PASSWORD_LENGTH} characters")

    for pattern, description in _STRENGTH_RULES:
        if not re.search(pattern, password):
            failures.append(description)

    if failures:
        detail = "Password must contain " + ", ".join(failures) + "."
        raise ValueError(detail)


def hash_password(password: str) -> str:
    """Hash a plain-text password for storage."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
