from fastapi import APIRouter, HTTPException, UploadFile, File
from app.schemas.document import DocumentUploadResponse, DocumentCategoriesResponse, DocumentCategory
from app.services.document_service import DocumentService
from app.services.queue_service import QueueService

router = APIRouter()
document_service = DocumentService()
queue_service = QueueService()

@router.post("/", response_model=DocumentUploadResponse, summary="Upload and Process Legal Document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a legal document.
    
    This endpoint implements the exact LangGraph workflow from GenrativeAICode/retrievel.py:
    - load_doc: Loads and parses PDF/TXT files
    - decision: Categorizes document (contracts vs policy) using AI
    - embed_and_store: Splits content and stores in vector database
    
    **RESTful Design**: POST /api/v1/documents (resource creation - creates a document resource)
    
    Supports: PDF and TXT files
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Process using exact LangGraph workflow
        result = await document_service.process_uploaded_file(file)
        
        return DocumentUploadResponse(
            filename=file.filename,
            file_path=result.get("file_path", "processed"),
            content_length=result.get("content_length", 0),
            category=result["category"],
            status=result["status"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/async", summary="Upload Document as Background Job")
async def upload_document_async(file: UploadFile = File(...)):
    """
    Upload and process a document as a background job.
    
    This endpoint submits document processing to the RQ queue system to prevent
    rate limiting and handle large document processing in the background.
    
    **Use this endpoint when:**
    - Processing large documents
    - Handling high upload volume
    - Want to prevent timeout issues
    
    **RESTful Design**: POST /api/v1/documents/async (background job creation)
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file content
        file_content = await file.read()
        content_str = file_content.decode('utf-8', errors='ignore')
        
        # Submit to background queue
        result = queue_service.submit_document_upload(
            file_content=content_str,
            filename=file.filename
        )
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        return {
            "job_id": result["job_id"],
            "status": result["status"],
            "message": result["message"],
            "estimated_wait_time": result["estimated_wait_time"],
            "filename": file.filename,
            "check_status_url": f"/api/v1/jobs/{result['job_id']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit async document upload: {str(e)}")


@router.get("/categories", response_model=DocumentCategoriesResponse, summary="Get Document Categories")
async def get_document_categories():
    """
    Get available document categories with examples.
    
    Returns the exact categories used in the decision function from GenrativeAICode/retrievel.py.
    
    **RESTful Design**: GET /api/v1/documents/categories (resource collection)
    """
    return DocumentCategoriesResponse(
        categories=[
            DocumentCategory(
                name="contracts",
                description="Legal contracts and agreements",
                examples=["employment_contract.txt", "service_agreement.txt", "nda.txt", "rent_agreement.txt"]
            ),
            DocumentCategory(
                name="policy", 
                description="Policy documents and terms",
                examples=["refund_policy.txt", "privacy_policy.txt", "terms_and_conditions.txt", "warranty_policy.txt"]
            )
        ]
    )

@router.get("/health", summary="Document Service Health Check")
async def get_document_health():
    """
    Get document processing service health status.
    
    **RESTful Design**: GET /api/v1/documents/health (resource inspection)
    """
    return {
        "service": "document_processing",
        "status": "active",
        "supported_formats": [".pdf", ".txt"],
        "workflow_steps": ["load_doc", "decision", "embed_and_store"],
        "categories": ["contracts", "policy"],
        "ai_model": "gemini-1.5-flash"
    }