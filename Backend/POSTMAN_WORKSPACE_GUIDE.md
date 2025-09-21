# 🚀 Complete Postman Workspace Guide - Queue System API

## 📋 System Overview

**Application Stack:**
- **FastAPI Server**: http://localhost:8000
- **Qdrant Vector DB**: http://localhost:6333
- **Valkey (Redis)**: localhost:6379
- **MongoDB**: localhost:27017
- **RQ Worker**: Background processing

## 🗄️ Database Configurations

### MongoDB Connection Details
```
Host: localhost
Port: 27017
Username: admin
Password: password
Database: legal_ai_jobs
Authentication Database: admin
```

### Collections in MongoDB
1. **job_tracking** - Stores all job status and metadata
2. **chat_history** - Chat query logs
3. **document_metadata** - Document upload tracking

## 📚 Postman Collections Structure

### Collection 1: 🏥 Health & Status Endpoints
**Base URL**: `http://localhost:8000`

#### Endpoints:
1. **GET** `/` - Root Health Check
   - **Purpose**: Verify API is running
   - **Response**: Welcome message
   - **Example Response**:
   ```json
   {
     "message": "Legal AI Backend API"
   }
   ```

2. **GET** `/health` - System Health Check
   - **Purpose**: Check all services status
   - **Response**: Health status of Valkey, MongoDB, Queue
   - **Example Response**:
   ```json
   {
     "status": "healthy",
     "services": {
       "valkey": "connected",
       "mongodb": "connected",
       "queue": "operational"
     }
   }
   ```

3. **GET** `/api/v1/health` - API Health Check
   - **Purpose**: API-specific health status
   - **Response**: API health information

---

### Collection 2: 📄 Document Management
**Base URL**: `http://localhost:8000/api/v1`

#### Endpoints:
1. **POST** `/documents/` - Upload Document
   - **Purpose**: Upload and process documents
   - **Content-Type**: `multipart/form-data`
   - **Body**: 
     ```
     file: [Select PDF file]
     ```
   - **Example Response**:
   ```json
   {
     "message": "Document uploaded successfully",
     "filename": "contract.pdf",
     "size": 245760,
     "document_id": "doc_12345"
   }
   ```

2. **GET** `/documents/` - List Documents
   - **Purpose**: Get all uploaded documents
   - **Response**: List of document metadata

3. **GET** `/documents/{document_id}` - Get Document Details
   - **Purpose**: Get specific document information
   - **Path Parameter**: `document_id` (string)

4. **DELETE** `/documents/{document_id}` - Delete Document
   - **Purpose**: Remove document from system
   - **Path Parameter**: `document_id` (string)

---

### Collection 3: 💬 Query Management
**Base URL**: `http://localhost:8000/api/v1`

#### Endpoints:
1. **POST** `/queries/` - Submit Query
   - **Purpose**: Submit legal question for processing
   - **Content-Type**: `application/json`
   - **Body**:
   ```json
   {
     "query": "What are the key terms in this contract?",
     "context": "contract analysis",
     "user_id": "user123"
   }
   ```
   - **Example Response**:
   ```json
   {
     "message": "Query submitted successfully",
     "query_id": "query_67890",
     "status": "processing"
   }
   ```

2. **GET** `/queries/` - List Queries
   - **Purpose**: Get all submitted queries
   - **Query Parameters**: 
     - `limit` (optional): Number of results
     - `offset` (optional): Pagination offset

3. **GET** `/queries/{query_id}` - Get Query Details
   - **Purpose**: Get specific query and response
   - **Path Parameter**: `query_id` (string)

---

### Collection 4: ⚡ Queue Job Management
**Base URL**: `http://localhost:8000/api/v1/jobs`

#### Endpoints:
1. **POST** `/jobs/submit-chat-job` - Submit Chat Job to Queue
   - **Purpose**: Add chat query to background processing queue
   - **Content-Type**: `application/json`
   - **Body**:
   ```json
   {
     "query": "Explain the legal implications of this clause",
     "user_id": "user123",
     "session_id": "session456"
   }
   ```
   - **Example Response**:
   ```json
   {
     "job_id": "job_abc123",
     "status": "queued",
     "queue_position": 2,
     "estimated_wait_time": 30
   }
   ```

2. **POST** `/jobs/submit-document-job` - Submit Document Job to Queue
   - **Purpose**: Add document processing to queue
   - **Content-Type**: `multipart/form-data`
   - **Body**:
   ```
   file: [Select file]
   metadata: {"document_type": "contract", "priority": "high"}
   ```

3. **GET** `/jobs/job-status/{job_id}` - Get Job Status
   - **Purpose**: Check status of queued job
   - **Path Parameter**: `job_id` (string)
   - **Example Response**:
   ```json
   {
     "job_id": "job_abc123",
     "status": "completed",
     "progress": 100,
     "result": {
       "response": "Analysis complete",
       "processing_time": 45.2
     },
     "created_at": "2025-09-21T10:30:00Z",
     "completed_at": "2025-09-21T10:30:45Z"
   }
   ```

4. **GET** `/jobs/queue-stats` - Get Queue Statistics
   - **Purpose**: Get queue performance metrics
   - **Example Response**:
   ```json
   {
     "chat_queue": {
       "pending_jobs": 3,
       "completed_jobs": 157,
       "failed_jobs": 2
     },
     "document_queue": {
       "pending_jobs": 1,
       "completed_jobs": 89,
       "failed_jobs": 0
     },
     "total_jobs_processed": 246,
     "average_processing_time": 32.5
   }
   ```

5. **DELETE** `/jobs/cancel-job/{job_id}` - Cancel Job
   - **Purpose**: Cancel a pending job
   - **Path Parameter**: `job_id` (string)

6. **POST** `/jobs/clear-failed` - Clear Failed Jobs
   - **Purpose**: Clear all failed and corrupted jobs from queues
   - **Response**: Cleanup operation results

---

## 🔧 Postman Environment Variables

Create an environment in Postman with these variables:

```json
{
  "base_url": "http://localhost:8000",
  "api_base": "http://localhost:8000/api/v1",
  "mongodb_host": "localhost:27017",
  "mongodb_user": "admin",
  "mongodb_pass": "password",
  "valkey_host": "localhost:6379"
}
```

## 📝 Testing Scenarios

### Scenario 1: Complete Document Processing Flow
1. **Health Check**: `GET /health`
2. **Upload Document**: `POST /api/v1/documents/`
3. **Submit Document Job**: `POST /api/v1/submit-document-job`
4. **Check Job Status**: `GET /api/v1/job-status/{job_id}`
5. **Get Queue Stats**: `GET /api/v1/queue-stats`

### Scenario 2: Chat Query Processing
1. **Submit Chat Query**: `POST /api/v1/queries/`
2. **Submit Chat Job**: `POST /api/v1/submit-chat-job`
3. **Monitor Job**: `GET /api/v1/job-status/{job_id}`
4. **Get Query Result**: `GET /api/v1/queries/{query_id}`

### Scenario 3: System Monitoring
1. **System Health**: `GET /health`
2. **Queue Statistics**: `GET /api/v1/queue-stats`
3. **List All Jobs**: `GET /api/v1/queries/`
4. **List Documents**: `GET /api/v1/documents/`

## 🎯 Sample Test Data

### Sample Chat Query
```json
{
  "query": "What are the termination clauses in employment contracts?",
  "context": "employment law research",
  "user_id": "tester_001"
}
```

### Sample Document Upload
- Use any PDF file (contracts, legal documents)
- Supported formats: PDF, DOC, DOCX
- Max file size: 10MB

## 🔍 MongoDB Direct Queries (Optional)

Connect to MongoDB using any client:

```javascript
// Check job status directly
db.job_tracking.find({"job_id": "your_job_id"})

// Get all completed jobs
db.job_tracking.find({"status": "completed"})

// Get queue statistics
db.job_tracking.aggregate([
  {$group: {
    _id: "$status",
    count: {$sum: 1}
  }}
])
```

## 🚨 Common Response Codes

- **200**: Success
- **201**: Created (for POST requests)
- **400**: Bad Request (invalid data)
- **404**: Not Found (invalid ID)
- **422**: Validation Error
- **500**: Internal Server Error

## 📊 Expected Response Times

- **Health checks**: < 100ms
- **Document upload**: 1-5 seconds
- **Query submission**: < 500ms
- **Job processing**: 30-120 seconds (varies by complexity)

## 🔧 Troubleshooting Guide

### Browser Not Showing Content
1. **Check Server Status**: Ensure FastAPI server is running on port 8000
   ```powershell
   # Start server if not running
   D:/google_hackathon/Backend/.venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Check Worker Status**: Ensure RQ worker is running
   ```powershell
   # Start worker if not running
   D:/google_hackathon/Backend/.venv/Scripts/python.exe Queue/worker.py
   ```

3. **Test Endpoints**: Use browser or curl to test
   - Root: http://localhost:8000
   - Health: http://localhost:8000/health
   - API Docs: http://localhost:8000/docs

### Common Issues
- **Connection Refused**: Server not running - start FastAPI server
- **404 Errors**: Check URL paths match the documented endpoints exactly
- **500 Errors**: Check MongoDB and Valkey are running via Docker
- **URL Encoding Issues**: Ensure no extra characters like %0A in URLs

### Quick Health Check Commands
```powershell
# Test API health
curl -X GET "http://localhost:8000/health"

# Test queue system
curl -X GET "http://localhost:8000/api/v1/jobs/queue-stats"

# Clear failed jobs if needed
curl -X POST "http://localhost:8000/api/v1/jobs/clear-failed"
```

---

**🎉 Ready to test!** Import these collections into Postman and start testing your queue system. All services should be running via Docker Compose before testing.