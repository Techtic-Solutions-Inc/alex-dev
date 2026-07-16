from fastapi import FastAPI, Request
from src.middlewares.error_handling import error_handling_middleware
from src.middlewares.rate_limiting import rate_limiting_middleware
from src.api.v1.routes.admin_update_user import router as admin_update_user_router
from src.api.v1.routes.request_password_reset import router as request_password_reset_router
from src.api.v1.routes.reset_password import router as reset_password_router

app = FastAPI()


@app.middleware('http')
async def apply_error_handling_middleware(request: Request, call_next):
    return await error_handling_middleware(request, call_next)


@app.middleware('http')
async def apply_rate_limiting_middleware(request: Request, call_next):
    return await rate_limiting_middleware(request, call_next)


app.include_router(request_password_reset_router, prefix='/api/v1')
app.include_router(reset_password_router, prefix='/api/v1')
app.include_router(admin_update_user_router, prefix='/api/v1')
