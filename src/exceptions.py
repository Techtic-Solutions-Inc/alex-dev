"""Shared application exceptions."""

from fastapi import HTTPException, status


class DuplicateEmailError(Exception):
    """Raised when attempting to register with an existing email."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


def duplicate_email_http_exception() -> HTTPException:
    """Return standardized duplicate email error response."""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already in use. Please use a different email address.",
    )


def invalid_credentials_http_exception() -> HTTPException:
    """Return standardized invalid credentials error response."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )
