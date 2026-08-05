"""API-layer registration service.

Orchestrates user registration by coordinating validation, core registration,
and confirmation email dispatch.  Delegates DB operations to the core
:mod:`services.auth` module and email delivery to :mod:`services.email_service`.
"""

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.validators.auth import validate_registration_input
from models.schema import RegisterRequest, RegisterResponse
from services.auth import register_user
from services.email_service import send_confirmation_email_async
from utils.token import generate_confirmation_token


async def create_registered_user(
    body: RegisterRequest, db: AsyncSession
) -> RegisterResponse:
    """Validate inputs, register a new user, and send a confirmation email.

    Runs the validators layer, delegates DB persistence to the core
    ``register_user`` service, then dispatches a confirmation email
    via SendGrid.
    """
    email = body.email.lower()
    await validate_registration_input(email, body.password, db)
    response = await register_user(body, db)

    confirmation_token = generate_confirmation_token(response.email)
    try:
        await send_confirmation_email_async(response.email, confirmation_token)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to send confirmation email.",
        ) from exc

    return response
