from fastapi import APIRouter, status, Query

from app.schemas.about import AboutRequest, AboutResponse
from app.schemas.common import ErrorResponse
from app.services.about_service import AboutService

router = APIRouter()

_COMMON_ERROR_RESPONSES = {
    400: {
        "description": "Invalid input or validation failure",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "examples": {
                    "validation_error": {
                        "summary": "Missing or invalid fields",
                        "value": {
                            "success": False,
                            "message": "Validation error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "phone",
                                        "message": "Field required",
                                    },
                                    {
                                        "field": "terms_accepted",
                                        "message": "Field required",
                                    },
                                ],
                            },
                        },
                    },
                    "invalid_phone": {
                        "summary": "Phone number format is invalid",
                        "value": {
                            "success": False,
                            "message": "Validation error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "phone",
                                        "message": (
                                            "Invalid phone number format"
                                        ),
                                    }
                                ],
                            },
                        },
                    },
                    "terms_not_accepted": {
                        "summary": "Terms checkbox not checked",
                        "value": {
                            "success": False,
                            "message": "Validation error",
                            "error": {
                                "code": "VALIDATION_ERROR",
                                "details": [
                                    {
                                        "field": "terms_accepted",
                                        "message": (
                                            "You must accept the Terms of Use "
                                            "and Privacy Policy"
                                        ),
                                    }
                                ],
                            },
                        },
                    },
                }
            }
        },
    },
    401: {
        "description": "Authentication required (not applicable; endpoint is public)",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Authentication required",
                    "error": {"code": "UNAUTHORIZED", "details": None},
                }
            }
        },
    },
    403: {
        "description": "Insufficient permissions (not applicable; endpoint is public)",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Access denied",
                    "error": {"code": "FORBIDDEN", "details": None},
                }
            }
        },
    },
    404: {
        "description": "About Us content not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "About Us content not found",
                    "error": {"code": "ABOUT_NOT_FOUND", "details": None},
                }
            }
        },
    },
    409: {
        "description": "Conflict (not applicable for this read endpoint)",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "Resource conflict",
                    "error": {"code": "CONFLICT", "details": None},
                }
            }
        },
    },
    422: {
        "description": "Validation error (not applicable; mapped to 400)",
        "model": ErrorResponse,
    },
    500: {
        "description": "Internal server error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "An unexpected error occurred",
                    "error": {
                        "code": "INTERNAL_SERVER_ERROR",
                        "details": None,
                    },
                }
            }
        },
    },
}


@router.get(
    "/",
    response_model=AboutResponse,
    status_code=status.HTTP_200_OK,
    summary="Get About Us page content",
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
        **_COMMON_ERROR_RESPONSES,
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
        **_COMMON_ERROR_RESPONSES,
    },
)
async def submit_contact_info(phone: str = Query(...), terms_accepted: bool = Query(...)) -> AboutResponse:
    """Submit contact information for the About Us page."""
    body = AboutRequest(phone=phone, terms_accepted=terms_accepted)
    service = AboutService()
    about_data = service.submit_contact_info(body)
    return AboutResponse(
        success=True,
        message="Contact information submitted successfully",
        data=about_data,
    )
