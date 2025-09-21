# Simple startup script without full Docker build
# Use this if having network connectivity issues with Docker images

Write-Host "=== Legal AI Assistant - Simple Startup ===" -ForegroundColor Green
Write-Host "Starting core services only: Qdrant and Valkey" -ForegroundColor Cyan
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
    Write-Host ""
}

# Stop any existing containers
Write-Host "🛑 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose down

# Start just the core services first
Write-Host "🚀 Starting core services (Qdrant, Valkey)..." -ForegroundColor Green

# Start Qdrant
Write-Host "   Starting Qdrant..." -ForegroundColor Yellow
docker run -d --name legal_ai_qdrant -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant

# Start Valkey
Write-Host "   Starting Valkey..." -ForegroundColor Yellow
docker run -d --name legal_ai_valkey -p 6379:6379 valkey/valkey:latest valkey-server --appendonly yes

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

# Check Valkey (Redis)
try {
    $connection = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet
    if ($connection) {
        Write-Host "✅ Valkey Queue System: Running" -ForegroundColor Green
    } else {
        Write-Host "❌ Valkey Queue System: Not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Valkey Queue System: Not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "Core services are running. Now start the FastAPI application:" -ForegroundColor White
Write-Host ""
Write-Host "1. Install dependencies:" -ForegroundColor Yellow
Write-Host "   pip install -r requirements.txt" -ForegroundColor White
Write-Host ""
Write-Host "2. Start FastAPI (in another terminal):" -ForegroundColor Yellow
Write-Host "   cd app" -ForegroundColor White
Write-Host "   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor White
Write-Host ""
Write-Host "3. Start RQ Worker (in another terminal):" -ForegroundColor Yellow
Write-Host "   python Queue/worker.py" -ForegroundColor White
Write-Host ""
Write-Host "=== Available Services ===" -ForegroundColor Cyan
Write-Host "📍 Qdrant: http://localhost:6333" -ForegroundColor White
Write-Host "🔄 Valkey: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "Note: MongoDB is skipped in this simple setup." -ForegroundColor Gray
Write-Host "The queue system will work but job tracking will be limited." -ForegroundColor Gray