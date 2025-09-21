from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """Request model for document queries - matches user_query function signature"""
    query: str = Field(..., min_length=1, description="Legal question or search query")
    category: Optional[str] = Field("category", description="Document category to search in (contracts/policy), defaults to 'category'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the termination conditions in employment contracts?",
                "category": "contracts"
            }
        }

class QueryResponse(BaseModel):
    """Response model for document queries - matches user_query function return"""
    query: str = Field(..., description="Original query")
    response: str = Field(..., description="AI-generated legal advice response")
    found_documents: int = Field(..., description="Number of relevant documents found")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the termination conditions in employment contracts?",
                "response": "Based on the employment contracts in your database, termination conditions typically include...",
                "found_documents": 3
            }
        }