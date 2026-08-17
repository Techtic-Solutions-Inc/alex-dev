from fastapi import APIRouter

router = APIRouter()

@router.get('/health', summary='Check service health', description='Returns the health status of the service.')
async def health_check():
    return {'status': 'healthy'}
