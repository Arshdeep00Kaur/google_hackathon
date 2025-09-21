from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import QueryService
from app.services.queue_service import QueueService

router = APIRouter()
query_service = QueryService()
queue_service = QueueService()

@router.post("/", response_model=QueryResponse, summary="Query Legal Documents")
async def query_documents(request: QueryRequest):
    """
    Query legal documents using AI assistance.
    
    This endpoint implements the exact logic from GenrativeAICode/query.py:
    - Searches vector database for relevant document chunks
    - Uses Google Gemini AI to provide simplified legal guidance
    - Returns AI response with document count
    
    **RESTful Design**: POST /api/v1/queries (resource creation - creates a query result)
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Call the exact user_query function logic
        result = query_service.user_query(
            query=request.query,
            category=request.category
        )
        
        return QueryResponse(
            query=result["query"],
            response=result["response"],
            found_documents=result["found_documents"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")


@router.post("/async", summary="Submit Query as Background Job")
async def submit_async_query(request: QueryRequest):
    """
    Submit a query as a background job for processing.
    
    This endpoint submits queries to the RQ queue system to prevent rate limiting
    and handle long-running AI processing in the background.
    
    **Use this endpoint when:**
    - You expect high traffic
    - You want to prevent rate limiting
    - You need to handle multiple concurrent queries
    
    **RESTful Design**: POST /api/v1/queries/async (background job creation)
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Submit query to background queue
        result = queue_service.submit_chat_query(
            query_text=request.query
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "job_id": result["job_id"],
            "status": result["status"],
            "message": result["message"],
            "estimated_wait_time": result["estimated_wait_time"],
            "query": request.query,
            "check_status_url": f"/api/v1/jobs/{result['job_id']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit async query: {str(e)}")


@router.get("/health", summary="Query Service Health Check")
async def get_query_health():
    """
    Get query service health status.
    
    **RESTful Design**: GET /api/v1/queries/health (resource inspection)
    """
    return {
        "service": "query_processing",
        "status": "active",
        "ai_model": "gemini-1.5-flash",
        "vector_database": "qdrant",
        "endpoint": "http://localhost:6333"
    }