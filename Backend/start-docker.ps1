# Complete Docker-based Startup Script for Legal AI Assistant
# This script starts the entire system using Docker containers

Write-Host "=== Legal AI Assistant - Complete Docker Setup ===" -ForegroundColor Green
Write-Host "Starting all services: Qdrant, Valkey, MongoDB, FastAPI, and RQ Worker" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the Backend directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Please run this script from the Backend directory" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check environment variables
if (-not $env:GEMINI_API_KEY) {
    Write-Host "⚠️  Warning: GEMINI_API_KEY environment variable not set" -ForegroundColor Yellow
    Write-Host "   Please set it: `$env:GEMINI_API_KEY='your-api-key'" -ForegroundColor Yellow
    Write-Host "   Some features may not work without it." -ForegroundColor Yellow
    Write-Host ""
}

# Stop any existing containers
Write-Host "🛑 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose down

# Build and start all services
Write-Host "🚀 Building and starting all services..." -ForegroundColor Green
docker-compose up --build -d

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service status
Write-Host "🔍 Checking service status..." -ForegroundColor Green

# Check Qdrant
try {
    $response = Invoke-WebRequest -Uri "http://localhost:6333/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Qdrant Vector Database: Running" -ForegroundColor Green
} catch {
    Write-Host "❌ Qdrant Vector Database: Not responding" -ForegroundColor Red
}

# Check FastAPI
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ FastAPI Backend: Running" -ForegroundColor Green
} catch {
    Write-Host "❌ FastAPI Backend: Not responding" -ForegroundColor Red
}

# Check Valkey (Redis)
try {
    # Check if port is listening
    $connection = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet
    if ($connection) {
        Write-Host "✅ Valkey Queue System: Running" -ForegroundColor Green
    } else {
        Write-Host "❌ Valkey Queue System: Not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Valkey Queue System: Not responding" -ForegroundColor Red
}

# Check MongoDB
try {
    $connection = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet
    if ($connection) {
        Write-Host "✅ MongoDB Job Tracking: Running" -ForegroundColor Green
    } else {
        Write-Host "❌ MongoDB Job Tracking: Not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ MongoDB Job Tracking: Not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== System URLs ===" -ForegroundColor Cyan
Write-Host "📍 FastAPI Backend: http://localhost:8000" -ForegroundColor White
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host "🔧 Queue Health Check: http://localhost:8000/api/v1/queue/health" -ForegroundColor White
Write-Host "💾 Qdrant Dashboard: http://localhost:6333/dashboard" -ForegroundColor White

Write-Host ""
Write-Host "=== Available API Endpoints ===" -ForegroundColor Cyan
Write-Host "Synchronous (immediate response):" -ForegroundColor Yellow
Write-Host "  POST /api/v1/queries - Process queries immediately" -ForegroundColor White
Write-Host "  POST /api/v1/documents - Upload documents immediately" -ForegroundColor White
Write-Host ""
Write-Host "Asynchronous (background jobs):" -ForegroundColor Yellow
Write-Host "  POST /api/v1/queries/async - Submit query as background job" -ForegroundColor White
Write-Host "  POST /api/v1/documents/async - Upload document as background job" -ForegroundColor White
Write-Host "  GET  /api/v1/jobs/{job_id} - Check job status and results" -ForegroundColor White
Write-Host "  GET  /api/v1/jobs - List recent jobs" -ForegroundColor White

Write-Host ""
Write-Host "=== Useful Commands ===" -ForegroundColor Cyan
Write-Host "View logs: docker-compose logs -f [service_name]" -ForegroundColor White
Write-Host "Stop system: docker-compose down" -ForegroundColor White
Write-Host "Restart system: docker-compose restart" -ForegroundColor White
Write-Host "View containers: docker-compose ps" -ForegroundColor White

Write-Host ""
if ($env:GEMINI_API_KEY) {
    Write-Host "🎉 System is ready! You can now use the Legal AI Assistant." -ForegroundColor Green
} else {
    Write-Host "⚠️  System started but GEMINI_API_KEY is not set." -ForegroundColor Yellow
    Write-Host "   Set it and restart: `$env:GEMINI_API_KEY='your-key'; docker-compose restart backend worker" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press Ctrl+C to view live logs or close this window to run in background." -ForegroundColor Gray

# Show live logs (user can Ctrl+C to exit)
try {
    docker-compose logs -f
} catch {
    Write-Host "Logs interrupted by user." -ForegroundColor Yellow
}