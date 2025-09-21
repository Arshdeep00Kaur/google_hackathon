from fastapi import APIRouter
from app.api.v1.endpoints import documents, queries, jobs

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(queries.router, prefix="/queries", tags=["queries"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

# Add queue health endpoint directly to avoid double prefix
from app.services.queue_service import QueueService
queue_service = QueueService()

@api_router.get("/queue/health", tags=["queue"])
async def get_queue_health():
    """Get queue system health information"""
    try:
        health_info = queue_service.get_queue_health()
        if health_info.get('overall_status') == 'error':
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail=health_info.get('error', 'Queue system unhealthy'))
        return health_info
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to get queue health: {str(e)}")