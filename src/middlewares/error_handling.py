from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

async def error_handling_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as exc:
        return JSONResponse(content={'detail': exc.detail}, status_code=exc.status_code)
    except Exception as e:
        return JSONResponse(content={'detail': str(e)}, status_code=500)
