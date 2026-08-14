from fastapi import APIRouter, Request, status

from app.core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.exceptions.http_exceptions import UnauthorizedException
from app.middleware.rate_limiter import limiter
from app.schemas.auth import RefreshTokenRequest, RefreshTokenResponse, TokenData
from app.schemas.common import ErrorResponse

router = APIRouter()


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description=(
        "Exchange a valid refresh token for a new access token and refresh token pair. "
        "The refresh token must be a JWT issued by this service with type `refresh`. "
        "No authentication header is required; pass the refresh token in the request body."
    ),
    tags=["Auth"],
    responses={
        200: {
            "description": "Tokens refreshed successfully",
            "model": RefreshTokenResponse,
        },
        401: {
            "description": "Invalid or expired refresh token",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Invalid or expired refresh token",
                        "error": {
                            "code": "INVALID_TOKEN",
                            "details": None,
                        },
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Validation error",
                        "error": {
                            "code": "VALIDATION_ERROR",
                            "details": [
                                {
                                    "field": "refresh_token",
                                    "message": "Field required",
                                }
                            ],
                        },
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "message": "Internal server error",
                        "error": {
                            "code": "INTERNAL_ERROR",
                            "details": None,
                        },
                    }
                }
            },
        },
    },
)
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
) -> RefreshTokenResponse:
    """Issue a new access/refresh token pair from a valid refresh token."""
    try:
        payload = verify_token(body.refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    except ValueError:
        raise UnauthorizedException(
            message="Invalid or expired refresh token",
            code="INVALID_TOKEN",
        )

    token_data = {
        "sub": payload["sub"],
        "role": payload.get("role", "user"),
    }
    access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)

    return RefreshTokenResponse(
        success=True,
        message="Token refreshed successfully",
        data=TokenData(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        ),
    )
