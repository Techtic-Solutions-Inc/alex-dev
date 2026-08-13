from fastapi import APIRouter

from app.api.v1.auth.router import auth_router
from app.api.v1.blog.router import router as blog_router
from app.api.v1.content.router import router as content_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# Blog CRUD is also mounted at /api/blog in main.py to match the public API contract.
api_router.include_router(blog_router, prefix="/blog", tags=["Blog"])
# Content CRUD is also mounted at /api/content in main.py to match the public API contract.
api_router.include_router(content_router, prefix="/content", tags=["Content"])
