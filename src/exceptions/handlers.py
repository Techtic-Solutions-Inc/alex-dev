"""Exception handlers for the FastAPI application."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from src.exceptions.http_exceptions import AppHTTPException
from src.schemas.responses import (
    ErrorResponse,
    ValidationErrorItem,
    ValidationErrorResponse,
)


def _build_error_response(
    *,
    message: str,
    code: str,
    details=None,
) -> dict:
    """Build a consistent error response payload."""
    return ErrorResponse(
        success=False,
        message=message,
        error={"code": code, "details": details},
    ).model_dump()


def register_exception_handlers(app: FastAPI) -> None:
    """Register global and custom exception handlers on the FastAPI app."""

    @app.exception_handler(AppHTTPException)
    async def app_http_exception_handler(
        request: Request,
        exc: AppHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_build_error_response(
                message=exc.message,
                code=exc.code,
                details=exc.details,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            location = error.get("loc", ())
            field = ".".join(str(part) for part in location if part != "body")
            errors.append(
                ValidationErrorItem(
                    field=field or "body",
                    message=error.get("msg", "Invalid value"),
                )
            )

        path = request.url.path.rstrip("/")

        # Signup ticket ACs require HTTP 400 (not FastAPI's default 422) with
        # stable field codes so Swagger Try-it-out + FE error handling stay aligned.
        # Covers both canonical `/api/auth/signup` and FE alias `/api/signup`.
        if path.endswith("/api/auth/signup") or path.endswith("/api/signup"):
            first = exc.errors()[0] if exc.errors() else {}
            loc = first.get("loc") or ()
            field = next(
                (str(part) for part in loc if part not in ("body",)),
                "body",
            )
            msg = str(first.get("msg") or "Invalid value")
            # Pydantic may prefix custom validator messages with "Value error, ".
            if msg.lower().startswith("value error,"):
                msg = msg.split(",", 1)[1].strip()

            code = "VALIDATION_ERROR"
            message = msg
            if field == "first_name":
                code, message = "MISSING_FIRST_NAME", "First name is required."
            elif field == "last_name":
                code, message = "MISSING_LAST_NAME", "Last name is required."
            elif field == "email":
                code, message = "INVALID_EMAIL", "Invalid email format."
            elif field == "password":
                code = "WEAK_PASSWORD"
                message = (
                    "Password must be at least 8 characters long and include an "
                    "uppercase letter, a number, and a special character."
                )
            elif field == "terms_accepted":
                code, message = (
                    "TERMS_NOT_ACCEPTED",
                    "You must accept the Terms of Use and Privacy Policy.",
                )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=_build_error_response(
                    message=message,
                    code=code,
                    details={"field": field},
                ),
            )

        # Login ticket ACs require HTTP 400 when email/password are empty or missing.
        if path.endswith("/api/auth/login") or path.endswith("/api/auth/signin"):
            first = exc.errors()[0] if exc.errors() else {}
            loc = first.get("loc") or ()
            field = next(
                (str(part) for part in loc if part not in ("body",)),
                "body",
            )
            msg = str(first.get("msg") or "Invalid value")
            # Pydantic may prefix custom validator messages with "Value error, ".
            if msg.lower().startswith("value error,"):
                msg = msg.split(",", 1)[1].strip()

            code = "VALIDATION_ERROR"
            message = msg
            lowered = msg.lower()
            if field == "email":
                if "required" in lowered or "field required" in lowered:
                    code, message = "EMPTY_EMAIL", "Email is required."
                else:
                    code, message = "INVALID_EMAIL", "Invalid email format."
            elif field == "password":
                if "required" in lowered or "field required" in lowered:
                    code, message = "EMPTY_PASSWORD", "Password is required."
                else:
                    code, message = "VALIDATION_ERROR", msg

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    **_build_error_response(
                        message=message,
                        code=code,
                        details={"field": field},
                    ),
                    "detail": message,
                    "errors": [
                        {"field": item.field, "message": item.message}
                        for item in errors
                    ],
                },
            )

        # Email verification ticket ACs require HTTP 400 for validation errors.
        if path.endswith("/api/email/verify"):
            first = exc.errors()[0] if exc.errors() else {}
            loc = first.get("loc") or ()
            field = next(
                (str(part) for part in loc if part not in ("body",)),
                "body",
            )
            msg = str(first.get("msg") or "Invalid value")
            if msg.lower().startswith("value error,"):
                msg = msg.split(",", 1)[1].strip()

            code = "VALIDATION_ERROR"
            message = msg
            lowered = msg.lower()
            if field == "email":
                if "required" in lowered or "field required" in lowered:
                    code, message = "EMPTY_EMAIL", "Email is required."
                else:
                    code, message = "INVALID_EMAIL", "Invalid email format."
            elif field == "terms_accepted":
                code, message = (
                    "TERMS_NOT_ACCEPTED",
                    "You must accept the Terms of Use and Privacy Policy.",
                )

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=_build_error_response(
                    message=message,
                    code=code,
                    details={"field": field},
                ),
            )

        # Password recovery ticket ACs require HTTP 400 for validation errors.
        if path.endswith("/api/password-recovery") or path.endswith(
            "/api/password-recovery/reset"
        ):
            first = exc.errors()[0] if exc.errors() else {}
            loc = first.get("loc") or ()
            field = next(
                (str(part) for part in loc if part not in ("body",)),
                "body",
            )
            msg = str(first.get("msg") or "Invalid value")
            if msg.lower().startswith("value error,"):
                msg = msg.split(",", 1)[1].strip()

            code = "VALIDATION_ERROR"
            message = msg
            lowered = msg.lower()
            if field == "email":
                if "required" in lowered or "field required" in lowered:
                    code, message = "EMPTY_EMAIL", "Email is required."
                else:
                    code, message = "INVALID_EMAIL", "Invalid email format."
            elif field == "password":
                code = "WEAK_PASSWORD"
                message = (
                    "Password must be at least 8 characters long and include an "
                    "uppercase letter, a number, and a special character."
                )
            elif field == "terms_accepted":
                code, message = (
                    "TERMS_NOT_ACCEPTED",
                    "You must accept the Terms of Use and Privacy Policy.",
                )
            elif field == "token":
                code, message = "INVALID_TOKEN", "A password reset token is required."

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=_build_error_response(
                    message=message,
                    code=code,
                    details={"field": field},
                ),
            )

        validation_response = ValidationErrorResponse(errors=errors)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                **_build_error_response(
                    message="Validation Error",
                    code="VALIDATION_ERROR",
                    details=validation_response.errors,
                ),
                "detail": validation_response.detail,
                "errors": [item.model_dump() for item in validation_response.errors],
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception for {} {}",
            request.method,
            request.url,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal Server Error",
                **_build_error_response(
                    message="Internal Server Error",
                    code="INTERNAL_SERVER_ERROR",
                    details=None,
                ),
            },
        )
