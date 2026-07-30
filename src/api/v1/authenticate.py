from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.middleware.rate_limiting import RateLimitStrategy, create_rate_limiter
from src.schemas.auth import AuthenticateRequest, AuthenticateResponse
from src.services.auth0_service import AuthenticationError
from src.services.user_service import UserService

router = APIRouter(prefix="/user", tags=["user"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db=db)


@router.post(
    "/authenticate",
    response_model=AuthenticateResponse,
    dependencies=[
        Depends(
            create_rate_limiter(
                requests=10,
                window_seconds=60,
                strategy=RateLimitStrategy.IP,
            )
        )
    ],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials",
            "content": {"application/json": {"example": {"detail": "Invalid email or password"}}},
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation error",
        },
    },
)
def authenticate_user(
    request: AuthenticateRequest,
    user_service: UserService = Depends(get_user_service),
) -> AuthenticateResponse:
    try:
        return user_service.authenticate(email=request.email, password=request.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc
