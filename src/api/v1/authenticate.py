from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.config import Settings, get_settings
from src.database import get_db
from src.models.user import User
from src.schemas.auth import AuthenticateRequest, AuthenticateResponse, ErrorResponse
from src.services.auth0 import Auth0AuthenticationError, Auth0Service

router = APIRouter(prefix="/user", tags=["user"])


def get_auth0_service(settings: Settings = Depends(get_settings)) -> Auth0Service:
    return Auth0Service(settings)


@router.post(
    "/authenticate",
    response_model=AuthenticateResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
    summary="Authenticate user with email and password",
)
async def authenticate_user(
    request: AuthenticateRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    auth0_service: Auth0Service = Depends(get_auth0_service),
) -> AuthenticateResponse:
    user = db.query(User).filter(User.email == request.email).first()

    if user is not None and not user.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials", "message": "Invalid email or password"},
        )

    try:
        token_data = await auth0_service.authenticate(request.email, request.password)
    except Auth0AuthenticationError as exc:
        status_code = (
            status.HTTP_503_SERVICE_UNAVAILABLE
            if exc.error_code == "service_unavailable"
            else status.HTTP_401_UNAUTHORIZED
        )
        raise HTTPException(
            status_code=status_code,
            detail={"error": exc.error_code, "message": exc.message},
        ) from exc

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_credentials", "message": "Invalid email or password"},
        )

    return AuthenticateResponse(
        access_token=access_token,
        token_type=token_data.get("token_type", "Bearer"),
        expires_in=token_data.get("expires_in", 86400),
        redirect_url=settings.dashboard_redirect_url,
        email=request.email,
    )
