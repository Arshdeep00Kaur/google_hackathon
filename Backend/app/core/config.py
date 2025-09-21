import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for basic configuration
        class BaseSettings:
            pass

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    EMBEDDING_MODEL: str = "models/embedding-001"
    
    # Qdrant Configuration
    QDRANT_URL: str = "http://localhost:6333"
    
    # Document Processing Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 300
    MAX_SEARCH_RESULTS: int = 5
    
    # Supported file types
    SUPPORTED_FILE_TYPES: list = [".pdf", ".txt"]
    
    # Document categories
    DOCUMENT_CATEGORIES: list = ["contracts", "policy"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()