"""JWT guard compatibility import for the FastAPI dependency model."""

from app.dependencies.auth import get_current_subject

JwtAuthGuard = get_current_subject

__all__ = ["JwtAuthGuard", "get_current_subject"]
