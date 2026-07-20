"""Application-wide exception types."""

from typing import Any


class AppException(Exception):
    """Base application exception with HTTP mapping metadata."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        error_code: str = "app_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(
            message,
            status_code=401,
            error_code="authentication_error",
        )


class AuthorizationError(AppException):
    def __init__(self, message: str = "Not authorized") -> None:
        super().__init__(
            message,
            status_code=403,
            error_code="authorization_error",
        )


class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            message,
            status_code=404,
            error_code="not_found",
        )


class ValidationError(AppException):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(
            message,
            status_code=422,
            error_code="validation_error",
        )
