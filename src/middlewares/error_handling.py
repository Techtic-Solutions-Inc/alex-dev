from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(content={'detail': str(e)}, status_code=500)
