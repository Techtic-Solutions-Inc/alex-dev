from typing import Any

from fastapi import status


class AppHTTPException(Exception):
    """Custom HTTP exception with a stable machine-readable error code."""

    def __init__(
        self,
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


class UnauthorizedException(AppHTTPException):
    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "UNAUTHORIZED",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            code=code,
            details=details,
        )


class ForbiddenException(AppHTTPException):
    def __init__(
        self,
        message: str = "Access denied",
        code: str = "FORBIDDEN",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            code=code,
            details=details,
        )


class NotFoundException(AppHTTPException):
    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            code=code,
            details=details,
        )


class ConflictException(AppHTTPException):
    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            code=code,
            details=details,
        )


class ValidationException(AppHTTPException):
    def __init__(
        self,
        message: str = "Validation error",
        code: str = "VALIDATION_ERROR",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            code=code,
            details=details,
        )


class BadRequestException(AppHTTPException):
    def __init__(
        self,
        message: str = "Bad request",
        code: str = "BAD_REQUEST",
        details: Any = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            code=code,
            details=details,
        )
