from src.api.v1.routes.auth_routes import router as auth_router
from src.api.v1.routes.health_routes import router as health_router

__all__ = ["auth_router", "health_router"]
