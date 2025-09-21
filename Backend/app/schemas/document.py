from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class DocumentUploadResponse(BaseModel):
    """Response model for document upload - matches LangGraph workflow result"""
    filename: str = Field(..., description="Name of the uploaded file")
    file_path: str = Field(..., description="Path where file was processed")
    content_length: int = Field(..., description="Length of extracted content")
    category: str = Field(..., description="Detected document category (contracts/policy/unknown)")
    status: str = Field(..., description="Processing status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "employment_contract.pdf",
                "file_path": "/tmp/tmpfile.pdf",
                "content_length": 1250,
                "category": "contracts",
                "status": "success"
            }
        }

class DocumentCategory(BaseModel):
    """Document category information"""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    examples: list = Field(..., description="Example document types")

class DocumentCategoriesResponse(BaseModel):
    """Response for available document categories"""
    categories: list[DocumentCategory] = Field(..., description="Available document categories")
    
    class Config:
        json_schema_extra = {
            "example": {
                "categories": [
                    {
                        "name": "contracts",
                        "description": "Legal contracts and agreements",
                        "examples": ["employment_contract.txt", "service_agreement.txt", "nda.txt", "rent_agreement.txt"]
                    },
                    {
                        "name": "policy",
                        "description": "Policy documents and terms",
                        "examples": ["refund_policy.txt", "privacy_policy.txt", "terms_and_conditions.txt", "warranty_policy.txt"]
                    }
                ]
            }
        }