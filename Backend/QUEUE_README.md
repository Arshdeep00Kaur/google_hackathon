# Queue System Documentation

## Overview

This Legal AI Assistant now includes a complete queue system to handle background jobs and prevent rate limiting. The system uses:

- **RQ (Redis Queue)** for job management
- **Valkey** (Redis alternative) for queue storage
- **MongoDB** for job tracking and persistence
- **Docker** for easy deployment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│   RQ Queue      │───▶│   RQ Worker     │
│   (Submits)     │    │   (Valkey)      │    │   (Processes)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MongoDB       │    │   Qdrant DB     │    │   Google AI     │
│   (Job Status)  │    │   (Vectors)     │    │   (Processing)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Start the Complete System

```powershell
# Set your Google API key
$env:GEMINI_API_KEY = "your-google-api-key-here"

# Start all services with Docker
.\start-docker.ps1
```

This will start:
- **Qdrant** (Vector Database) on port 6333
- **Valkey** (Queue System) on port 6379
- **MongoDB** (Job Tracking) on port 27017
- **FastAPI** (Backend API) on port 8000
- **RQ Worker** (Background Processor)

### 2. Test the System

```powershell
# Run the queue system tests
python test_queue.py
```

## API Endpoints

### Synchronous (Immediate Response)
- `POST /api/v1/queries` - Process queries immediately
- `POST /api/v1/documents` - Upload documents immediately

### Asynchronous (Background Jobs)
- `POST /api/v1/queries/async` - Submit query as background job
- `POST /api/v1/documents/async` - Upload document as background job
- `GET /api/v1/jobs/{job_id}` - Check job status and results
- `GET /api/v1/jobs` - List recent jobs
- `GET /api/v1/queue/health` - Check queue system health

## Usage Examples

### Submit Async Query

```python
import requests

# Submit query as background job
response = requests.post("http://localhost:8000/api/v1/queries/async", 
                        json={"query": "What are employment contract requirements?"})

job_data = response.json()
job_id = job_data["job_id"]

# Check job status
status_response = requests.get(f"http://localhost:8000/api/v1/jobs/{job_id}")
print(status_response.json())
```

### Submit Async Document Upload

```python
import requests

# Upload document as background job
with open("contract.txt", "rb") as f:
    files = {"file": ("contract.txt", f, "text/plain")}
    response = requests.post("http://localhost:8000/api/v1/documents/async", files=files)

job_data = response.json()
job_id = job_data["job_id"]

# Monitor job progress
status_response = requests.get(f"http://localhost:8000/api/v1/jobs/{job_id}")
```

### Check Queue Health

```python
import requests

health = requests.get("http://localhost:8000/api/v1/queue/health").json()
print(f"Queue Status: {health['overall_status']}")
print(f"Valkey Connected: {health['queue_system']['valkey_connected']}")
print(f"MongoDB Connected: {health['mongodb_connected']}")
```

## Job Status Flow

1. **pending** - Job submitted to queue
2. **running** - Worker is processing the job
3. **completed** - Job finished successfully
4. **failed** - Job encountered an error

## Environment Variables

```env
# Required
GEMINI_API_KEY=your-google-api-key

# Queue System (Docker automatically sets these)
VALKEY_HOST=valkey
VALKEY_PORT=6379
VALKEY_DB=0

# MongoDB (Docker automatically sets these)
MONGODB_URL=mongodb://admin:password@mongodb:27017/
MONGODB_DATABASE=legal_ai_jobs

# Vector Database
QDRANT_URL=http://qdrant:6333
```

## Benefits of Queue System

### Rate Limiting Prevention
- Background processing prevents API rate limits
- Multiple workers can process jobs concurrently
- Failed jobs can be retried automatically

### Better User Experience
- Immediate response with job ID
- Users can check progress asynchronously
- No timeout issues for long-running tasks

### Scalability
- Easy to add more workers
- Job persistence in MongoDB
- Queue monitoring and statistics

## Monitoring

### View Logs
```powershell
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f worker
docker-compose logs -f backend
```

### Check Service Status
```powershell
# Check running containers
docker-compose ps

# Check queue health
curl http://localhost:8000/api/v1/queue/health
```

### Job Statistics
```powershell
# Get job statistics
curl http://localhost:8000/api/v1/jobs/stats

# List recent jobs
curl http://localhost:8000/api/v1/jobs
```

## Troubleshooting

### Common Issues

1. **Queue not connecting**
   - Check if Valkey container is running: `docker-compose ps`
   - Check logs: `docker-compose logs valkey`

2. **Jobs stuck in pending**
   - Check if worker is running: `docker-compose logs worker`
   - Restart worker: `docker-compose restart worker`

3. **MongoDB connection issues**
   - Check container: `docker-compose logs mongodb`
   - Verify credentials in docker-compose.yml

4. **Jobs failing**
   - Check if GEMINI_API_KEY is set correctly
   - View worker logs: `docker-compose logs worker`

### Reset System
```powershell
# Stop all containers
docker-compose down

# Remove volumes (clears all data)
docker-compose down -v

# Restart fresh
.\start-docker.ps1
```

## File Structure

```
Backend/
├── Queue/                  # Queue system implementation
│   ├── __init__.py
│   ├── connection.py       # Valkey connection and queue setup
│   └── worker.py          # Background job processing
├── app/
│   ├── models/
│   │   └── job_tracking.py # MongoDB models for job tracking
│   ├── services/
│   │   └── queue_service.py # Queue integration service
│   └── api/v1/endpoints/
│       └── jobs.py        # Job management API endpoints
├── docker-compose.yml     # All services configuration
├── Dockerfile            # Application container
├── start-docker.ps1      # Complete system startup
└── test_queue.py         # Queue system test suite
```

## Production Considerations

For production deployment:

1. **Security**: Change MongoDB credentials
2. **Persistence**: Use named volumes for data
3. **Monitoring**: Add health checks and alerting
4. **Scaling**: Increase worker replicas
5. **Backup**: Implement MongoDB backup strategy

## Advanced Usage

### Add More Workers
```yaml
# In docker-compose.yml
worker-2:
  build: .
  # ... same config as worker
  command: python Queue/worker.py
```

### Custom Queue Names
```python
# In worker.py, add custom job functions
def process_custom_job(job_id, data):
    # Your custom processing logic
    pass

# In queue_service.py, add custom submission
def submit_custom_job(self, data):
    custom_queue = get_queue('custom')
    # Submit to custom queue
```

This queue system provides a robust foundation for scaling the Legal AI Assistant while maintaining reliability and preventing rate limiting issues.