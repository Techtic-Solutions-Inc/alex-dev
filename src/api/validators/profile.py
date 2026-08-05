import re

from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, status

from models.schema import ProfileUpdateRequest

MOBILE_NUMBER_RE = re.compile(r"^\+?[1-9]\d{6,14}$")


def _validate_email_format(email: str) -> None:
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format.",
        )


def validate_profile_update(body: ProfileUpdateRequest) -> None:
    """Validate fields in a profile update request.

    Raises HTTPException(400) when a field value is invalid.
    """
    update_data = body.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        _validate_email_format(update_data["email"])

    if "mobile_number" in update_data and update_data["mobile_number"] is not None:
        if not MOBILE_NUMBER_RE.match(update_data["mobile_number"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid mobile number format.",
            )

    if "first_name" in update_data and update_data["first_name"] is not None:
        if not update_data["first_name"].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="First name cannot be empty.",
            )

    if "last_name" in update_data and update_data["last_name"] is not None:
        if not update_data["last_name"].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Last name cannot be empty.",
            )
