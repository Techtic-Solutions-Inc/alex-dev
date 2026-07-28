from fastapi import APIRouter, HTTPException, status

from src.config.settings import DASHBOARD_URL
from src.models.auth import AuthenticateRequest, AuthenticateResponse
from src.services.auth_service import AuthenticationError, authenticate_with_auth0
from src.utils.logger import logger

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/authenticate",
    response_model=AuthenticateResponse,
    summary="Authenticate user",
    description="Authenticate a user with email and password via Auth0.",
    responses={
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"},
    },
)
async def authenticate(request: AuthenticateRequest) -> AuthenticateResponse:
    logger.info("Authentication attempt for email=%s", request.email)
    try:
        token_data = authenticate_with_auth0(request.email, request.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    access_token = token_data.get("access_token")
    if not access_token:
        logger.error("Auth0 response missing access_token for email=%s", request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return AuthenticateResponse(
        access_token=access_token,
        token_type=token_data.get("token_type", "Bearer"),
        redirect_url=DASHBOARD_URL,
    )
