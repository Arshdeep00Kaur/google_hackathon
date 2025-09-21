# FastAPI Backend

A RESTful API implementation of the GenrativeAICode functionality using FastAPI, preserving the exact logic from the original `query.py` and `retrieval.py` files.

## Features

- **Document Upload**: Upload documents for processing and categorization
- **Document Querying**: Query uploaded documents using vector search and AI responses
- **Document Categories**: Retrieve available document categories (contracts, policy)
- **Vector Database**: Qdrant vector database for document embeddings
- **AI Integration**: Google Gemini AI for document classification and query responses

## Quick Start

### Prerequisites

- Python 3.8+
- Docker Desktop (for Qdrant database)
- Google API Key (for Gemini AI)

### Setup

1. **Set Environment Variable**:
   ```powershell
   $env:GOOGLE_API_KEY = "your-google-api-key-here"
   ```

2. **Start the System**:
   ```powershell
   cd Backend
   .\start-server.ps1
   ```

   This script will:
   - Start Qdrant database in Docker
   - Create Python virtual environment
   - Install dependencies
   - Start FastAPI server

### Manual Setup

If you prefer manual setup:

1. **Start Qdrant Database**:
   ```powershell
   docker-compose up -d
   ```

2. **Create Virtual Environment**:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start FastAPI Server**:
   ```powershell
   cd app
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

### Base URL: `http://localhost:8000/api/v1`

### 1. Document Upload
- **POST** `/documents`
- Upload a document file for processing
- **Form Data**: `file` (multipart/form-data)
- **Response**: Processing result with category

### 2. Query Documents
- **POST** `/queries`
- Query uploaded documents
- **Body**: `{"query": "your question here"}`
- **Response**: AI-generated answer based on document content

### 3. Get Categories
- **GET** `/documents/categories`
- Retrieve available document categories
- **Response**: List of categories

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

Run the test suite:
```powershell
python test_api.py
```

## Architecture

### Services
- **DocumentService**: Handles document processing using LangGraph workflow
- **QueryService**: Handles document querying using vector search and AI

### Key Components
- **FastAPI**: REST API framework
- **Qdrant**: Vector database for embeddings
- **LangChain**: Document processing and vector operations
- **Google Gemini**: AI for classification and query responses
- **LangGraph**: Workflow orchestration

### Exact Logic Preservation

This implementation preserves the exact logic from the original GenrativeAICode:
- Same system prompts and AI models
- Identical document processing workflow
- Same vector search and embedding logic
- Preserved document categorization rules

## Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Required for Google Gemini AI

### Qdrant Database
- Host: localhost
- Port: 6333
- Collection: "documents"

## Troubleshooting

### Common Issues

1. **Qdrant Connection Error**:
   - Ensure Docker is running
   - Check `docker-compose ps` to verify Qdrant is up

2. **Google API Key Error**:
   - Verify `GOOGLE_API_KEY` environment variable is set
   - Check API key permissions for Gemini AI

3. **Import Errors**:
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

### Logs
- FastAPI logs are displayed in the terminal
- Qdrant logs: `docker-compose logs qdrant`

## Development

### Project Structure
```
Backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── api/v1/              # API routes
│   ├── services/            # Business logic
│   ├── schemas/             # Pydantic models
│   ├── models/              # Data models
│   └── core/                # Configuration
├── docker-compose.yml       # Qdrant database
├── requirements.txt         # Python dependencies
├── start-server.ps1         # Startup script
└── test_api.py             # Test suite
```

### Adding New Endpoints
1. Create schema in `schemas/`
2. Add business logic in `services/`
3. Create endpoint in `api/v1/endpoints/`
4. Register router in `api/v1/router.py`