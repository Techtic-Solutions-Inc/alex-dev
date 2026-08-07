"""Authentication routes."""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.api.models.user import User
from src.api.services.auth0_service import get_auth0_service
from src.api.services.auth_service import (
    build_login_response_data,
    build_session_response_data,
    login_user,
)
from src.config.database import get_db
from src.exceptions import UnauthorizedError
from src.middlewares.auth import get_current_user_record
from src.schemas.auth import (
    LoginRequest,
    LoginSuccessResponse,
    SessionSuccessResponse,
)
from src.utils.token import generate_access_token

router = APIRouter()

_LOGIN_OPENAPI_RESPONSES = {
    201: {
        "description": "Successful sign-in returns a JWT access token.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Signed in successfully.",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 3600,
                        "title": "Welcome back",
                        "message": "You have signed in successfully.",
                        "description": (
                            "Everything you need to create standout real estate content."
                        ),
                        "link": "/dashboard",
                        "redirect": "/dashboard",
                    },
                }
            }
        },
    },
    400: {
        "description": "Empty or invalid login fields.",
        "content": {
            "application/json": {
                "examples": {
                    "empty_email": {
                        "summary": "Empty email",
                        "value": {
                            "success": False,
                            "message": "Email is required.",
                            "error": {
                                "code": "EMPTY_EMAIL",
                                "details": {"field": "email"},
                            },
                        },
                    },
                    "empty_password": {
                        "summary": "Empty password",
                        "value": {
                            "success": False,
                            "message": "Password is required.",
                            "error": {
                                "code": "EMPTY_PASSWORD",
                                "details": {"field": "password"},
                            },
                        },
                    },
                    "invalid_email": {
                        "summary": "Invalid email format",
                        "value": {
                            "success": False,
                            "message": "Invalid email format.",
                            "error": {
                                "code": "INVALID_EMAIL",
                                "details": {"field": "email"},
                            },
                        },
                    },
                }
            }
        },
    },
    401: {
        "description": "Authentication service unavailable or unauthorized.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication service is temporarily unavailable.",
                    "error": {
                        "code": "AUTHENTICATION_SERVICE_ERROR",
                        "details": None,
                    },
                }
            }
        },
    },
    403: {
        "description": "Forbidden.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "You do not have permission to perform this action.",
                    "error": {"code": "FORBIDDEN", "details": None},
                }
            }
        },
    },
    409: {
        "description": "Incorrect email or password.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Incorrect email or password.",
                    "error": {"code": "INCORRECT_PASSWORD", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Request body validation error.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Validation Error",
                    "error": {"code": "VALIDATION_ERROR", "details": None},
                    "detail": "Validation Error",
                    "errors": [
                        {"field": "email", "message": "Field required"},
                        {"field": "password", "message": "Field required"},
                    ],
                }
            }
        },
    },
    500: {
        "description": "Unexpected server error.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal Server Error",
                    "success": False,
                    "message": "Internal Server Error",
                    "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
                }
            }
        },
    },
}

_SESSION_OPENAPI_RESPONSES = {
    200: {
        "description": "Session is valid.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Session is valid.",
                    "data": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "title": "Session active",
                        "message": "Your session is active.",
                        "description": "You are signed in to Agentwise.",
                        "link": "/dashboard",
                        "redirect": "/dashboard",
                    },
                }
            }
        },
    },
    401: {
        "description": "Invalid or expired authentication token.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Invalid or expired token.",
                    "error": {"code": "UNAUTHORIZED", "details": None},
                }
            },
        },
    },
    403: {
        "description": "Missing JWT token or forbidden access to session information.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication is required to access this resource.",
                    "error": {"code": "FORBIDDEN", "details": None},
                }
            }
        },
    },
    404: {
        "description": "Authenticated user was not found.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "The requested resource was not found.",
                    "error": {"code": "NOT_FOUND", "details": None},
                }
            }
        },
    },
    500: {
        "description": "Unexpected server error.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Internal Server Error",
                    "success": False,
                    "message": "Internal Server Error",
                    "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
                }
            }
        },
    },
}


def _session_payload(current_user: User) -> dict:
    """Return the standard session success envelope."""
    return {
        "success": True,
        "message": "Session is valid.",
        "data": build_session_response_data(current_user),
    }


def _perform_login(request: LoginRequest, db: Session) -> dict:
    """Authenticate credentials and issue a JWT access token."""
    user, expires_in = login_user(
        db,
        email=request.email,
        password=request.password,
        remember_me=request.remember_me,
    )

    token = generate_access_token(
        {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
        },
        expires_in_seconds=expires_in,
    )

    return {
        "success": True,
        "message": "Signed in successfully.",
        "data": build_login_response_data(
            user,
            access_token=token,
            expires_in=expires_in,
        ),
    }


@router.post(
    "/api/auth/login",
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign in with email and password",
    description=(
        "Authenticate a user with their email address and password. "
        "When Auth0 is configured, credentials are validated against Auth0 before "
        "issuing a local JWT access token. "
        "Returns a JWT access token on success (HTTP 201). "
        "Set `remember_me` to true to extend the session lifetime for returning users. "
        "Empty email or password fields return HTTP 400. "
        "Incorrect password attempts return HTTP 409. "
        "No authentication is required."
    ),
    responses=_LOGIN_OPENAPI_RESPONSES,
    tags=["Authentication"],
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Authenticate credentials and issue a JWT access token."""
    return _perform_login(request, db)


@router.post(
    "/api/auth/signin",
    response_model=LoginSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign in with email and password (alias)",
    description=(
        "Alias of `POST /api/auth/login` for frontend Sign In form compatibility. "
        "Authenticate a user with their email address and password and return a JWT "
        "access token. Empty fields return HTTP 400; incorrect password returns "
        "HTTP 409. No authentication is required."
    ),
    responses=_LOGIN_OPENAPI_RESPONSES,
    tags=["Authentication"],
)
def signin(
    request: LoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Frontend-compatible alias for the login endpoint."""
    return _perform_login(request, db)


@router.get(
    "/api/auth/session",
    response_model=SessionSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current user session",
    description=(
        "Return the authenticated user's session details from the JWT supplied in "
        "the Authorization header. Requires a valid Bearer token. "
        "Missing tokens return HTTP 403; invalid or expired tokens return HTTP 401."
    ),
    responses=_SESSION_OPENAPI_RESPONSES,
    tags=["Authentication"],
)
def get_session(
    current_user: User = Depends(get_current_user_record),
) -> dict:
    """Retrieve the current authenticated user session."""
    return _session_payload(current_user)


@router.get(
    "/api/auth/validate",
    response_model=SessionSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate the current user session",
    description=(
        "Validate the JWT access token supplied in the Authorization header and "
        "return the authenticated user's session details. "
        "Requires a valid Bearer token. "
        "Missing tokens return HTTP 403; invalid or expired tokens return HTTP 401."
    ),
    responses=_SESSION_OPENAPI_RESPONSES,
    tags=["Authentication"],
)
def validate_session(
    current_user: User = Depends(get_current_user_record),
) -> dict:
    """Validate the current JWT session and return user details."""
    return _session_payload(current_user)


@router.post(
    "/api/auth/auth0/webhook",
    status_code=status.HTTP_200_OK,
    summary="Receive Auth0 webhook events",
    description=(
        "Handle Auth0 webhook callbacks for authentication lifecycle events. "
        "When `AUTH0_WEBHOOK_SECRET` is configured, the `X-Auth0-Signature` header "
        "must match the HMAC-SHA256 signature of the raw request body. "
        "No authentication is required."
    ),
    responses={
        200: {
            "description": "Webhook accepted.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Webhook processed.",
                        "data": {"received": True},
                    }
                }
            },
        },
        401: {
            "description": "Invalid webhook signature.",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Invalid webhook signature.",
                        "error": {"code": "UNAUTHORIZED", "details": None},
                    }
                }
            },
        },
        500: {
            "description": "Unexpected server error.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal Server Error",
                        "success": False,
                        "message": "Internal Server Error",
                        "error": {"code": "INTERNAL_SERVER_ERROR", "details": None},
                    }
                }
            },
        },
    },
    tags=["Authentication"],
)
async def auth0_webhook(request: Request) -> dict:
    """Process Auth0 webhook events."""
    body = await request.body()
    auth0_service = get_auth0_service()
    signature = request.headers.get("X-Auth0-Signature")

    if not auth0_service.verify_webhook_signature(body, signature):
        raise UnauthorizedError(
            message="Invalid webhook signature.",
            code="UNAUTHORIZED",
        )

    return {
        "success": True,
        "message": "Webhook processed.",
        "data": {"received": True},
    }
