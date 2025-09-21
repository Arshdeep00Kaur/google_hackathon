from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

# Create FastAPI application
app = FastAPI(
    title="Legal Document AI Assistant",
    description="API for processing legal documents and providing AI-powered legal advice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include API routes - handle import errors gracefully
try:
    from app.api.v1.router import api_router
    app.include_router(api_router, prefix="/api/v1")
except ImportError as e:
    print(f"Warning: Could not import API router: {e}")
    # Create a simple health endpoint if imports fail
    pass

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Legal Document AI Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )