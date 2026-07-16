from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.v1.schemas.auth import RequestPasswordResetRequest, RequestPasswordResetResponse
from src.api.v1.services.auth_service import AuthService
from src.database import get_db

router = APIRouter(tags=['auth'])


@router.post(
    '/email/reset',
    response_model=RequestPasswordResetResponse,
    summary='Request a password reset link',
    description=(
        'Validate the email address and send a password reset link if the account exists. '
        'The response is the same whether or not the email is registered.'
    ),
    responses={
        500: {'description': 'Failed to send password reset email'},
    },
)
async def request_password_reset(
    request: RequestPasswordResetRequest,
    db: Session = Depends(get_db),
) -> RequestPasswordResetResponse:
    auth_service = AuthService(db)
    try:
        return await auth_service.request_password_reset(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
