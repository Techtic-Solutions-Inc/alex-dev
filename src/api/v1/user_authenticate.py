from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.deps import get_auth_service, get_db
from src.schemas.auth import AuthenticateRequest, AuthenticateResponse
from src.services.auth_service import AuthService, AuthenticationError

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/authenticate",
    response_model=AuthenticateResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user with email and password",
)
def authenticate_user(
    payload: AuthenticateRequest,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthenticateResponse:
    try:
        session = auth_service.authenticate_user(
            db=db,
            email=payload.email,
            password=payload.password,
        )
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return AuthenticateResponse(
        access_token=session.access_token,
        token_type=session.token_type,
        expires_in=session.expires_in,
        redirect_url=session.redirect_url,
    )
