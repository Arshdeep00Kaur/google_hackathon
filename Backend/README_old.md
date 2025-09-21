# Backend Folder Structure

This folder contains the FastAPI application that exposes the document processing and query functionality as RESTful endpoints.

## Structure

- **app/**: Main application package
  - **main.py**: FastAPI application entry point
  - **core/**: Core configuration and settings
  - **api/v1/**: API version 1 routes and endpoints
  - **schemas/**: Pydantic models for request/response validation
  - **services/**: Business logic layer
  - **models/**: Data models and state definitions

## Key Features

1. **Document Processing**: Upload and categorize legal documents (contracts, policies)
2. **Query Processing**: Search documents and get AI-powered legal advice
3. **Vector Storage**: Integrate with Qdrant for document embeddings
4. **AI Integration**: Use Google Gemini for document analysis and responses

## API Endpoints

- `POST /api/v1/documents/upload` - Upload and process documents
- `POST /api/v1/queries/search` - Search documents and get AI responses
- `GET /api/v1/documents/categories` - Get available document categories

## Environment Variables

Required environment variables:
- `GEMINI_API_KEY`: Google Gemini API key
- `QDRANT_URL`: Qdrant vector database URL (default: http://localhost:6333)