"""Liveness and readiness endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.db.mongo import get_database
from app.exceptions.http_exceptions import APIException
from app.schemas.common import ErrorResponse, SuccessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    summary="Check API liveness and database readiness",
    description=(
        "Confirms that the API is running and can reach MongoDB. "
        "Returns `503 DATABASE_UNAVAILABLE` when the database cannot be reached."
    ),
    response_model=SuccessResponse[dict[str, str]],
    responses={
        400: {"model": ErrorResponse, "description": "Malformed request."},
        401: {"model": ErrorResponse, "description": "Authentication is not required."},
        403: {"model": ErrorResponse, "description": "Authorization is not required."},
        404: {"model": ErrorResponse, "description": "Route was not found."},
        409: {"model": ErrorResponse, "description": "No conflict is expected."},
        422: {"model": ErrorResponse, "description": "No request fields are accepted."},
        500: {"model": ErrorResponse, "description": "Unexpected server error."},
        503: {"model": ErrorResponse, "description": "MongoDB is unavailable."},
    },
)
def check_health(
    database: Annotated[Database, Depends(get_database)],
) -> SuccessResponse[dict[str, str]]:
    """Expose a readiness probe suitable for load balancers and monitoring."""
    try:
        database.command("ping")
    except PyMongoError as exc:
        raise APIException(
            "Database service is temporarily unavailable.", 503, "DATABASE_UNAVAILABLE"
        ) from exc
    return SuccessResponse(
        message="Service is healthy.", data={"status": "UP", "database": "UP"}
    )
