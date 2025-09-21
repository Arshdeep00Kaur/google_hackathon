# 🚀 Complete Backend System Documentation
## For Frontend Development

---

## 📋 **System Overview**

### **Architecture Type**: Microservices with Queue-Based Processing
### **Tech Stack**: FastAPI + MongoDB + Valkey/Redis + Qdrant + RQ Workers
### **Purpose**: Legal AI Document Processing and Query System with Rate Limiting Prevention

---

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   FastAPI       │───▶│   RQ Worker     │
│   (To Build)    │    │   Server        │    │   Background    │
└─────────────────┘    │   Port: 8000    │    │   Processing    │
                       └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                   ┌─────────────────┐    ┌─────────────────┐
                   │   MongoDB       │    │   Valkey/Redis  │
                   │   Port: 27017   │    │   Port: 6379    │
                   │   Job Tracking  │    │   Queue Storage │
                   └─────────────────┘    └─────────────────┘
                              │
                              ▼
                   ┌─────────────────┐
                   │   Qdrant        │
                   │   Port: 6333    │
                   │   Vector Search │
                   └─────────────────┘
```

---

## 🌐 **API Endpoints Reference**

### **Base URL**: `http://localhost:8000`

### **1. Health & Status Endpoints**

#### `GET /`
- **Purpose**: Root health check
- **Response**: Welcome message
- **Response Schema**:
  ```json
  {
    "message": "Legal AI Backend API"
  }
  ```

#### `GET /health`
- **Purpose**: System-wide health check
- **Response Schema**:
  ```json
  {
    "status": "healthy",
    "services": {
      "valkey": "connected",
      "mongodb": "connected", 
      "queue": "operational"
    },
    "timestamp": "2025-09-21T10:30:00Z"
  }
  ```

#### `GET /api/v1/health`
- **Purpose**: API-specific health
- **Response**: API health information

---

### **2. Document Management** (`/api/v1/documents/`)

#### `POST /api/v1/documents/`
- **Purpose**: Upload and process legal documents
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  ```
  file: <PDF/TXT file> (max 10MB)
  ```
- **Response Schema**:
  ```json
  {
    "filename": "contract.pdf",
    "file_path": "processed",
    "content_length": 245760,
    "category": "contracts",  // "contracts" | "policy" | "unknown"
    "status": "processed"
  }
  ```
- **Error Responses**:
  - `400`: Invalid file or no filename
  - `500`: Processing failure

#### `GET /api/v1/documents/`
- **Purpose**: List all uploaded documents
- **Query Parameters**:
  - `limit` (optional): Number of results (default: 10)
  - `offset` (optional): Pagination offset (default: 0)
- **Response Schema**:
  ```json
  {
    "documents": [
      {
        "document_id": "doc_12345",
        "filename": "contract.pdf",
        "category": "contracts",
        "upload_date": "2025-09-21T10:30:00Z",
        "size": 245760,
        "status": "processed"
      }
    ],
    "total": 25,
    "limit": 10,
    "offset": 0
  }
  ```

#### `GET /api/v1/documents/{document_id}`
- **Purpose**: Get specific document details
- **Path Parameter**: `document_id` (string)
- **Response Schema**:
  ```json
  {
    "document_id": "doc_12345",
    "filename": "contract.pdf",
    "category": "contracts",
    "content_preview": "First 500 characters...",
    "metadata": {
      "pages": 5,
      "word_count": 1200,
      "created_date": "2025-09-21T10:30:00Z"
    },
    "processing_info": {
      "ai_classification": "contracts",
      "vector_stored": true,
      "processing_time": 45.2
    }
  }
  ```

#### `DELETE /api/v1/documents/{document_id}`
- **Purpose**: Delete document from system
- **Path Parameter**: `document_id` (string)
- **Response Schema**:
  ```json
  {
    "message": "Document deleted successfully",
    "document_id": "doc_12345"
  }
  ```

---

### **3. Query Management** (`/api/v1/queries/`)

#### `POST /api/v1/queries/`
- **Purpose**: Submit legal question for processing
- **Content-Type**: `application/json`
- **Request Schema**:
  ```json
  {
    "query": "What are the key terms in this contract?",
    "context": "contract analysis",           // optional
    "user_id": "user123",                     // required
    "category": "contracts"                   // optional: "contracts" | "policy"
  }
  ```
- **Response Schema**:
  ```json
  {
    "query_id": "query_67890",
    "status": "processing",                   // "processing" | "completed" | "failed"
    "submitted_at": "2025-09-21T10:30:00Z",
    "estimated_completion": "2025-09-21T10:31:00Z"
  }
  ```

#### `GET /api/v1/queries/`
- **Purpose**: List all submitted queries
- **Query Parameters**:
  - `limit` (optional): Number of results
  - `offset` (optional): Pagination offset
  - `user_id` (optional): Filter by user
  - `status` (optional): Filter by status
- **Response Schema**:
  ```json
  {
    "queries": [
      {
        "query_id": "query_67890",
        "query": "What are the key terms?",
        "user_id": "user123",
        "status": "completed",
        "submitted_at": "2025-09-21T10:30:00Z",
        "completed_at": "2025-09-21T10:30:45Z"
      }
    ],
    "total": 15,
    "limit": 10,
    "offset": 0
  }
  ```

#### `GET /api/v1/queries/{query_id}`
- **Purpose**: Get specific query and response
- **Path Parameter**: `query_id` (string)
- **Response Schema**:
  ```json
  {
    "query_id": "query_67890",
    "query": "What are the key terms in this contract?",
    "user_id": "user123",
    "category": "contracts",
    "status": "completed",
    "response": {
      "answer": "The key terms include...",
      "sources": [
        {
          "document_id": "doc_12345",
          "page": 2,
          "relevance_score": 0.95
        }
      ],
      "confidence": 0.92
    },
    "processing_info": {
      "submitted_at": "2025-09-21T10:30:00Z",
      "completed_at": "2025-09-21T10:30:45Z",
      "processing_time": 45.2
    }
  }
  ```

---

### **4. Queue Job Management** (`/api/v1/jobs/`)

#### `POST /api/v1/jobs/submit-chat-job`
- **Purpose**: Submit chat query to background queue
- **Content-Type**: `application/json`
- **Request Schema**:
  ```json
  {
    "query": "Explain the legal implications of this clause",
    "user_id": "user123",
    "session_id": "session456",              // optional
    "priority": "normal"                     // "low" | "normal" | "high"
  }
  ```
- **Response Schema**:
  ```json
  {
    "job_id": "job_abc123",
    "status": "queued",                      // "queued" | "processing" | "completed" | "failed"
    "queue_position": 2,
    "estimated_wait_time": 30,               // seconds
    "submitted_at": "2025-09-21T10:30:00Z"
  }
  ```

#### `POST /api/v1/jobs/submit-document-job`
- **Purpose**: Submit document processing to queue
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  ```
  file: <document file>
  metadata: {"document_type": "contract", "priority": "high"}
  ```
- **Response**: Same as chat job response

#### `GET /api/v1/jobs/job-status/{job_id}`
- **Purpose**: Check status of queued job
- **Path Parameter**: `job_id` (string)
- **Response Schema**:
  ```json
  {
    "job_id": "job_abc123",
    "type": "chat_query",                    // "chat_query" | "document_processing"
    "status": "completed",                   // "queued" | "processing" | "completed" | "failed" | "cancelled"
    "progress": 100,                         // 0-100
    "result": {
      "response": "Analysis complete",
      "data": { /* specific result data */ }
    },
    "error": null,                           // error message if failed
    "timestamps": {
      "created_at": "2025-09-21T10:30:00Z",
      "started_at": "2025-09-21T10:30:05Z",
      "completed_at": "2025-09-21T10:30:45Z"
    },
    "processing_info": {
      "processing_time": 45.2,
      "worker_id": "worker_001",
      "attempts": 1
    }
  }
  ```

#### `GET /api/v1/jobs/queue-stats`
- **Purpose**: Get queue performance metrics
- **Response Schema**:
  ```json
  {
    "chat_queue": {
      "pending_jobs": 3,
      "processing_jobs": 1,
      "completed_jobs": 157,
      "failed_jobs": 2,
      "avg_processing_time": 35.5
    },
    "document_queue": {
      "pending_jobs": 1,
      "processing_jobs": 0,
      "completed_jobs": 89,
      "failed_jobs": 0,
      "avg_processing_time": 65.8
    },
    "total_stats": {
      "total_jobs_processed": 246,
      "success_rate": 0.98,
      "average_processing_time": 42.3,
      "uptime": "15h 32m"
    },
    "workers": {
      "active_workers": 2,
      "total_workers": 3,
      "worker_status": [
        {
          "worker_id": "worker_001",
          "status": "busy",
          "current_job": "job_abc123",
          "jobs_completed": 45
        }
      ]
    }
  }
  ```

#### `DELETE /api/v1/jobs/cancel-job/{job_id}`
- **Purpose**: Cancel a pending job
- **Path Parameter**: `job_id` (string)
- **Response Schema**:
  ```json
  {
    "message": "Job cancelled successfully",
    "job_id": "job_abc123",
    "status": "cancelled"
  }
  ```

#### `POST /api/v1/jobs/clear-failed`
- **Purpose**: Clear all failed jobs from queues
- **Response Schema**:
  ```json
  {
    "message": "Failed jobs cleanup completed",
    "result": {
      "cleared_queues": [
        {
          "queue": "chat",
          "failed_jobs_cleared": 3,
          "status": "cleared"
        }
      ],
      "errors": [],
      "cleared_keys": 5
    },
    "timestamp": "2025-09-21T10:30:00Z"
  }
  ```

---

## 🗄️ **Database Schemas**

### **MongoDB Connection Details**
```
Host: localhost:27017
Database: legal_ai_jobs
Username: admin
Password: password
Auth Database: admin
Connection String: mongodb://admin:password@localhost:27017/legal_ai_jobs?authSource=admin
```

### **Collections & Schemas**

#### **1. job_tracking Collection**
```json
{
  "_id": "ObjectId",
  "job_id": "job_abc123",
  "job_type": "chat_query",              // "chat_query" | "document_processing"
  "status": "completed",                 // "queued" | "processing" | "completed" | "failed" | "cancelled"
  "user_id": "user123",
  "session_id": "session456",
  "input_data": {
    "query": "What are the legal terms?",
    "category": "contracts",
    "file_info": {                       // for document jobs
      "filename": "contract.pdf",
      "size": 245760
    }
  },
  "result_data": {
    "response": "Analysis complete",
    "confidence": 0.92,
    "sources": [
      {
        "document_id": "doc_123",
        "relevance": 0.95
      }
    ]
  },
  "error_info": {
    "error_type": "processing_error",
    "error_message": "Failed to process",
    "stack_trace": "..."
  },
  "metadata": {
    "priority": "normal",
    "attempts": 1,
    "worker_id": "worker_001",
    "processing_time": 45.2,
    "queue_wait_time": 5.3
  },
  "timestamps": {
    "created_at": "2025-09-21T10:30:00Z",
    "started_at": "2025-09-21T10:30:05Z",
    "completed_at": "2025-09-21T10:30:45Z",
    "updated_at": "2025-09-21T10:30:45Z"
  }
}
```

#### **2. chat_history Collection**
```json
{
  "_id": "ObjectId",
  "query_id": "query_67890",
  "user_id": "user123",
  "session_id": "session456",
  "conversation": [
    {
      "role": "user",
      "message": "What are the key terms?",
      "timestamp": "2025-09-21T10:30:00Z"
    },
    {
      "role": "assistant", 
      "message": "The key terms include...",
      "sources": ["doc_123"],
      "confidence": 0.92,
      "timestamp": "2025-09-21T10:30:45Z"
    }
  ],
  "metadata": {
    "category": "contracts",
    "total_messages": 2,
    "total_processing_time": 45.2
  },
  "timestamps": {
    "created_at": "2025-09-21T10:30:00Z",
    "updated_at": "2025-09-21T10:30:45Z"
  }
}
```

#### **3. document_metadata Collection**
```json
{
  "_id": "ObjectId",
  "document_id": "doc_12345",
  "filename": "contract.pdf",
  "original_filename": "employment_contract.pdf",
  "file_info": {
    "size": 245760,
    "mime_type": "application/pdf",
    "hash": "sha256_hash_here"
  },
  "content_info": {
    "page_count": 5,
    "word_count": 1200,
    "character_count": 8500,
    "language": "en"
  },
  "processing_info": {
    "status": "processed",               // "uploaded" | "processing" | "processed" | "failed"
    "category": "contracts",             // "contracts" | "policy" | "unknown"
    "ai_classification_confidence": 0.95,
    "vector_stored": true,
    "processing_time": 65.8
  },
  "vector_info": {
    "collection_name": "contracts",
    "chunks_created": 12,
    "embedding_model": "models/embedding-001"
  },
  "user_info": {
    "uploaded_by": "user123",
    "upload_session": "session456"
  },
  "timestamps": {
    "uploaded_at": "2025-09-21T10:30:00Z",
    "processed_at": "2025-09-21T10:31:05Z",
    "updated_at": "2025-09-21T10:31:05Z"
  }
}
```

---

## ⚡ **Queue System Details**

### **Queue Types**
1. **chat** - Chat query processing
2. **documents** - Document upload processing  
3. **default** - General background tasks

### **Job Types & Data**

#### **Chat Job Data Structure**
```json
{
  "job_type": "chat_query",
  "input": {
    "query": "What are the termination clauses?",
    "user_id": "user123",
    "session_id": "session456",
    "category": "contracts",
    "context": "employment law"
  },
  "config": {
    "priority": "normal",
    "timeout": 300,
    "max_retries": 3
  }
}
```

#### **Document Job Data Structure**
```json
{
  "job_type": "document_processing", 
  "input": {
    "file_path": "/tmp/contract.pdf",
    "filename": "contract.pdf",
    "user_id": "user123",
    "metadata": {
      "document_type": "contract",
      "priority": "high"
    }
  },
  "config": {
    "priority": "high",
    "timeout": 600,
    "max_retries": 2
  }
}
```

### **Job Status Lifecycle**
```
queued → processing → completed
                  ↓
                failed
                  ↓
              cancelled (manual)
```

---

## 🎯 **AI Processing Details**

### **Document Classification**
- **Input**: Document content (first 2000 characters)
- **Output**: Category ("contracts" | "policy" | "unknown")
- **Model**: Gemini 1.5 Flash
- **Confidence Scoring**: 0.0 - 1.0

### **Vector Embeddings**
- **Model**: models/embedding-001 (Google)
- **Dimensions**: 768
- **Chunk Size**: 1000 characters
- **Overlap**: 300 characters
- **Storage**: Qdrant vector database

### **Query Processing**
- **Retrieval**: Similarity search (top 5 results)
- **Context Building**: Page content + metadata
- **Response Generation**: Gemini 1.5 Flash
- **Source Attribution**: Document references with page numbers

---

## 🔧 **Configuration & Environment**

### **Required Environment Variables**
```bash
# Google AI Configuration
GEMINI_API_KEY=your_api_key_here

# Database Configuration
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=legal_ai_jobs
MONGO_USER=admin
MONGO_PASSWORD=password

# Queue Configuration  
VALKEY_HOST=localhost
VALKEY_PORT=6379
VALKEY_DB=0

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### **Service Ports**
- **FastAPI**: 8000
- **MongoDB**: 27017  
- **Valkey/Redis**: 6379
- **Qdrant**: 6333

---

## 📊 **Error Handling & Status Codes**

### **HTTP Status Codes**
- **200**: Success
- **201**: Created (POST requests)
- **400**: Bad Request (validation error)
- **404**: Not Found (invalid ID)
- **422**: Unprocessable Entity (schema validation)
- **500**: Internal Server Error
- **503**: Service Unavailable (queue/database down)

### **Error Response Schema**
```json
{
  "detail": "Error message description",
  "error_code": "PROCESSING_FAILED",
  "timestamp": "2025-09-21T10:30:00Z",
  "request_id": "req_12345"
}
```

---

## 🎨 **Frontend Development Guidelines**

### **Recommended UI Components**

#### **1. Dashboard Overview**
- System health status indicators
- Queue statistics (pending, processing, completed)
- Recent activity feed
- Performance metrics graphs

#### **2. Document Management**
- File upload area (drag & drop)
- Document list with filters (category, date, status)
- Document preview modal
- Processing status indicators

#### **3. Query Interface**  
- Chat-style query input
- Query history sidebar
- Real-time response streaming
- Source document references

#### **4. Job Monitoring**
- Job queue status table
- Real-time job progress bars
- Job cancellation controls
- Error log viewer

### **Key User Workflows**

#### **Document Upload Flow**
1. User selects file → validation
2. Upload starts → progress indicator
3. Processing begins → queue position shown
4. AI classification → category badge
5. Vector storage → completion status
6. Document available for queries

#### **Query Processing Flow**
1. User types question → real-time validation
2. Submit to queue → estimated wait time
3. Processing status → progress updates
4. AI generates response → streaming display
5. Sources highlighted → clickable references
6. Save to history → shareable link

### **Real-time Features to Implement**
- WebSocket connections for job status updates
- Live queue position updates
- Real-time chat responses
- System health monitoring
- Progress indicators for long-running tasks

### **State Management Needs**
- User session management
- Job status tracking
- Document library state
- Query history
- System settings/preferences

---

## 🔄 **WebSocket Events (Recommended)**

### **Connection**: `ws://localhost:8000/ws/{user_id}`

### **Event Types**
```json
// Job Status Update
{
  "event": "job_status_update",
  "data": {
    "job_id": "job_abc123",
    "status": "processing",
    "progress": 45
  }
}

// Queue Position Update
{
  "event": "queue_position_update", 
  "data": {
    "job_id": "job_abc123",
    "position": 2,
    "estimated_wait": 30
  }
}

// Chat Response Streaming
{
  "event": "chat_response_chunk",
  "data": {
    "query_id": "query_67890",
    "chunk": "The contract terms include...",
    "is_final": false
  }
}

// System Alert
{
  "event": "system_alert",
  "data": {
    "level": "warning",
    "message": "Queue processing delayed",
    "timestamp": "2025-09-21T10:30:00Z"
  }
}
```

---

## 📈 **Performance Characteristics**

### **Expected Response Times**
- **Health checks**: < 100ms
- **Document upload**: 1-5 seconds
- **Query submission**: < 500ms  
- **Job processing**: 30-120 seconds
- **Vector search**: 200-800ms

### **Capacity Limits**
- **File size**: 10MB maximum
- **Concurrent jobs**: 5 per queue
- **Query length**: 1000 characters
- **Document chunks**: 12 per document average

### **Scalability Notes**
- Horizontal scaling via multiple workers
- Queue partitioning by priority
- Database indexing on frequently queried fields
- Vector database collection separation by category

---

**📝 This documentation provides complete context for building a comprehensive frontend that integrates with all backend functionalities, handles real-time updates, and provides excellent user experience for legal document processing and AI-powered queries.**