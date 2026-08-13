from fastapi import APIRouter

from app.api.v1.about.router import router as about_router
from app.api.v1.announcements.router import router as announcements_router
from app.api.v1.auth.router import auth_router
from app.api.v1.blog.router import router as blog_router
from app.api.v1.content.router import router as content_router
from app.api.v1.content_library.router import router as content_library_router
from app.api.v1.profile.router import router as profile_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# Announcements CRUD is also mounted at /api/announcements in main.py.
api_router.include_router(
    announcements_router,
    prefix="/announcements",
    tags=["Announcements"],
)
# Blog CRUD is also mounted at /api/blog in main.py to match the public API contract.
api_router.include_router(blog_router, prefix="/blog", tags=["Blog"])
# Content CRUD is also mounted at /api/content in main.py to match the public API contract.
api_router.include_router(content_router, prefix="/content", tags=["Content"])
api_router.include_router(profile_router, prefix="/profile", tags=["Profile"])
# About Us is also mounted at /api/about in main.py to match the public API contract.
api_router.include_router(about_router, prefix="/about", tags=["About"])
# Content Library is also mounted at /api/content-library in main.py.
api_router.include_router(
    content_library_router,
    prefix="/content-library",
    tags=["Content Library"],
)
