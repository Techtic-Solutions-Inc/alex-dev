"""Application exceptions that map to stable API error envelopes."""

from typing import Any


class APIException(Exception):
    """Base exception containing only safe client-facing details."""

    def __init__(
        self,
        message: str,
        status_code: int,
        code: str,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details


class HttpException(APIException):
    """Backward-compatible generic HTTP application exception."""

    def __init__(self, message: str, status: int) -> None:
        super().__init__(message, status, "HTTP_ERROR")
