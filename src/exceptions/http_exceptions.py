"""Custom HTTP exception classes."""

from typing import Any


class AppHTTPException(Exception):
    """Base application HTTP exception with structured error metadata."""

    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        code: str,
        details: Any = None,
    ) -> None:
        self.status_code = status_code
        self.message = message
        self.code = code
        self.details = details
        super().__init__(message)


class BadRequestError(AppHTTPException):
    """400 Bad Request."""

    def __init__(
        self,
        message: str = "The request could not be processed.",
        *,
        code: str = "BAD_REQUEST",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=400,
            message=message,
            code=code,
            details=details,
        )


class UnauthorizedError(AppHTTPException):
    """401 Unauthorized."""

    def __init__(
        self,
        message: str = "Authentication is required to access this resource.",
        *,
        code: str = "UNAUTHORIZED",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=401,
            message=message,
            code=code,
            details=details,
        )


class ForbiddenError(AppHTTPException):
    """403 Forbidden."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        *,
        code: str = "FORBIDDEN",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=403,
            message=message,
            code=code,
            details=details,
        )


class NotFoundError(AppHTTPException):
    """404 Not Found."""

    def __init__(
        self,
        message: str = "The requested resource was not found.",
        *,
        code: str = "NOT_FOUND",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=404,
            message=message,
            code=code,
            details=details,
        )


class ConflictError(AppHTTPException):
    """409 Conflict."""

    def __init__(
        self,
        message: str = "The request conflicts with the current state of the resource.",
        *,
        code: str = "CONFLICT",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=409,
            message=message,
            code=code,
            details=details,
        )


class ValidationAppError(AppHTTPException):
    """422 Validation Error."""

    def __init__(
        self,
        message: str = "Validation Error",
        *,
        code: str = "VALIDATION_ERROR",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=422,
            message=message,
            code=code,
            details=details,
        )


class InternalServerError(AppHTTPException):
    """500 Internal Server Error."""

    def __init__(
        self,
        message: str = "Internal Server Error",
        *,
        code: str = "INTERNAL_SERVER_ERROR",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=500,
            message=message,
            code=code,
            details=details,
        )
