from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Basic health check for monitoring.",
)
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
