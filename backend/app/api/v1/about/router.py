from fastapi import APIRouter, status

from app.schemas.about import AboutResponse
from app.services.about_service import AboutService

router = APIRouter()

@router.get(
    "/",
    response_model=AboutResponse,
    status_code=status.HTTP_200_OK,
    summary="Get About Us content",
    description=(
        "Retrieves content for the About Us screen in the Real Estate "
        "Professional module, including team members (Meet Our Team), "
        "marketing copy, and contact fields. This endpoint is **public** — "
        "no authentication is required."
    ),
    tags=["About"],
    responses={
        200: {
            "description": "About Us content retrieved successfully",
            "model": AboutResponse,
        },
    },
)
async def get_about() -> AboutResponse:
    """Return About Us page content (public)."""
    service = AboutService()
    about_data = service.get_about_content()
    return AboutResponse(
        success=True,
        message="About Us content retrieved successfully",
        data=about_data,
    )

@router.post(
    "/contact",
    response_model=AboutResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit contact information",
    description=(
        "Submits contact information for the About Us page. Requires "
        "`phone` and `terms_accepted` fields."
    ),
    tags=["About"],
    responses={
        200: {
            "description": "Contact information submitted successfully",
            "model": AboutResponse,
        },
    },
)
async def submit_contact_info(phone: str, terms_accepted: bool) -> AboutResponse:
    """Submit contact information for the About Us page."""
    body = AboutRequest(phone=phone, terms_accepted=terms_accepted)
    service = AboutService()
    about_data = service.submit_contact_info(body)
    return AboutResponse(
        success=True,
        message="Contact information submitted successfully",
        data=about_data,
    )
