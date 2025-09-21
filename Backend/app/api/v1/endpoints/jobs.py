"""
Queue Management API Endpoints

API endpoints for managing background jobs and queue system monitoring.
Simple and beginner-friendly implementation.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from app.services.queue_service import QueueService
from app.schemas.query import QueryRequest
import time

router = APIRouter()

# Initialize queue service
queue_service = QueueService()


@router.post("/chat")
async def submit_chat_job(query_request: QueryRequest, user_id: Optional[str] = None):
    """
    Submit a chat query as a background job
    
    Args:
        query_request: Query request with user's question
        user_id: Optional user identifier
        
    Returns:
        Job submission result with job_id for tracking
    """
    try:
        result = queue_service.submit_chat_query(
            query_text=query_request.query,
            user_id=user_id
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit chat job: {str(e)}")


@router.post("/document")
async def submit_document_job(file_content: str, filename: str, user_id: Optional[str] = None):
    """
    Submit a document upload as a background job
    
    Args:
        file_content: Document content as string
        filename: Name of the uploaded file
        user_id: Optional user identifier
        
    Returns:
        Job submission result with job_id for tracking
    """
    try:
        result = queue_service.submit_document_upload(
            file_content=file_content,
            filename=filename,
            user_id=user_id
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit document job: {str(e)}")


@router.post("/health-check")
async def submit_health_check_job():
    """
    Submit a health check job for testing the queue system
    
    Returns:
        Job submission result with job_id for tracking
    """
    try:
        result = queue_service.submit_health_check()
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit health check: {str(e)}")


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status and result of a specific job
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        Job status, result, and metadata
    """
    try:
        result = queue_service.get_job_status(job_id)
        
        if result.get('status') == 'not_found':
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")


@router.get("/")
async def get_recent_jobs(limit: int = 20):
    """
    Get recent jobs for monitoring
    
    Args:
        limit: Maximum number of jobs to return (default: 20, max: 100)
        
    Returns:
        List of recent jobs with their status and results
    """
    try:
        # Limit the number of jobs to prevent overload
        if limit > 100:
            limit = 100
        
        result = queue_service.get_recent_jobs(limit)
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent jobs: {str(e)}")


@router.post("/cleanup")
async def cleanup_old_jobs(days: int = 7):
    """
    Clean up old completed/failed jobs
    
    Args:
        days: Remove jobs older than this many days (default: 7)
        
    Returns:
        Cleanup result with number of jobs removed
    """
    try:
        # Limit days to prevent accidental deletion of recent jobs
        if days < 1:
            days = 1
        if days > 30:
            days = 30
        
        result = queue_service.cleanup_old_jobs(days)
        
        if result.get('status') == 'error':
            raise HTTPException(status_code=500, detail=result.get('error', 'Cleanup failed'))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup jobs: {str(e)}")


@router.get("/stats")
async def get_job_statistics():
    """
    Get job statistics and system overview
    
    Returns:
        Job statistics including counts by status and system health
    """
    try:
        health_info = queue_service.get_queue_health()
        
        # Extract relevant statistics
        stats = {
            'job_statistics': health_info.get('job_statistics', {}),
            'queue_system_status': health_info.get('queue_system', {}),
            'mongodb_connected': health_info.get('mongodb_connected', False),
            'overall_status': health_info.get('overall_status', 'unknown'),
            'timestamp': health_info.get('timestamp', time.time())
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job statistics: {str(e)}")


# Simple endpoint for checking if queue API is working
@router.get("/ping")
async def ping_queue_api():
    """
    Simple ping endpoint to check if queue API is working
    
    Returns:
        Simple pong response
    """
    return {
        "message": "Queue API is working!",
        "timestamp": time.time(),
        "status": "healthy"
    }


@router.post("/clear-failed")
async def clear_failed_jobs():
    """
    Clear failed and corrupted jobs from all queues
    
    Returns:
        Results of the cleanup operation
    """
    try:
        from Queue.connection import clear_failed_jobs
        result = clear_failed_jobs()
        return {
            "message": "Failed jobs cleanup completed",
            "result": result,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear jobs: {str(e)}")