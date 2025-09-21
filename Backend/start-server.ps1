# FastAPI Backend Startup Script
# Run this script to start the complete system

Write-Host "=== FastAPI Backend Startup ===" -ForegroundColor Green

# Check if we're in the Backend directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ Please run this script from the Backend directory" -ForegroundColor Red
    exit 1
}

# Start Qdrant database
Write-Host "🚀 Starting Qdrant database..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Qdrant database" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Qdrant database started" -ForegroundColor Green

# Wait for Qdrant to be ready
Write-Host "⏳ Waiting for Qdrant to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Check environment variables
if (-not $env:GOOGLE_API_KEY) {
    Write-Host "⚠️  Warning: GOOGLE_API_KEY environment variable not set" -ForegroundColor Yellow
    Write-Host "   Please set it before running queries: `$env:GOOGLE_API_KEY='your-api-key'" -ForegroundColor Yellow
}

# Start FastAPI server
Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Green
Write-Host "   API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Documentation at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

cd app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload