"""Authentication routes."""

from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
import hmac
import hashlib
from src.api.models.user import User
from src.api.services.auth0_service import Auth0AuthenticationService
from src.api.services.auth_service import (
    build_login_response_data,
    build_session_response_data,
    get_auth0_service_dependency,
    login_user,
)
from src.config.database import get_db
from src.schemas.auth import (
    LoginRequest,
    LoginSuccessResponse,
    SessionSuccessResponse,
)
from src.utils.token import generate_access_token
from src.config.settings import AUTH0_WEBHOOK_SECRET

router = APIRouter()

_SESSION_OPENAPI_RESPONSES = {
    200: {
        "description": "Session details retrieved successfully.",
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "message": "Session is valid.",
                    "data": {
                        "user": {
                            "id": "user_id",
                            "email": "user@example.com",
                            "username": "username",
                        },
                        "expires_in": 3600,
                    },
                }
            }
        },
    },
    404: {
        "description": "Resource not found.",
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

def _perform_login(
    request: LoginRequest,
    db: Session,
    auth0_service: Auth0AuthenticationService,
) -> dict:
    """Authenticate credentials and issue a JWT access token."""
    user, expires_in = login_user(
        db,
        email=request.email,
        password=request.password,
        remember_me=request.remember_me,
        auth0_service=auth0_service,
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
    auth0_service: Auth0AuthenticationService = Depends(get_auth0_service_dependency),
) -> dict:
    """Authenticate credentials and issue a JWT access token."""
    return _perform_login(request, db, auth0_service)

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
    auth0_service: Auth0AuthenticationService = Depends(get_auth0_service_dependency),
) -> dict:
    """Frontend-compatible alias for the login endpoint."""
    return _perform_login(request, db, auth0_service)

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
                        "error": {"code": "INVALID_SIGNATURE", "details": None},
                    }
                }
            },
        },
    },
    tags=["Authentication"],
)
async def auth0_webhook(request: Request):
    """Process Auth0 webhook events."""
    raw_body = await request.body()
    signature = request.headers.get("X-Auth0-Signature")

    if not signature:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing signature header")

    expected_signature = hmac.new(
        AUTH0_WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    # Process the webhook event
    return {
        "success": True,
        "message": "Webhook processed.",
        "data": {"received": True},
    }
