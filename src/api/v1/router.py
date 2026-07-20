from fastapi import APIRouter, FastAPI

from src.api.v1.health import router as health_router

router = APIRouter()
router.include_router(health_router, tags=["health"])

app = FastAPI(title="API")
app.include_router(router)
