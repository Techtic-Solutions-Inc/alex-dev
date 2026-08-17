"""Domain HTTP exceptions with stable machine-readable codes."""

from typing import Any


class AppHTTPException(Exception):
    """An expected API error that can be safely returned to a client."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)
