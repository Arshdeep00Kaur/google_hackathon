# run-local.ps1 - Start the Legal AI Assistant

Write-Host "Starting Legal AI Assistant..." -ForegroundColor Green

# Start Qdrant vector database
Write-Host "Starting Qdrant vector database..." -ForegroundColor Green
docker-compose up -d

# Wait for Qdrant to be ready
Write-Host "Waiting for Qdrant to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test Qdrant connection
Write-Host "Testing Qdrant connection..." -ForegroundColor Green
try {
    $response = Invoke-WebRequest -Uri "http://localhost:6333/" -UseBasicParsing
    Write-Host "✅ Qdrant is running successfully!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Warning: Could not connect to Qdrant. Please check if it's running." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Green
pip install -r requirements.txt

# Run FastAPI application
Write-Host "Starting FastAPI application..." -ForegroundColor Green
Write-Host "📍 API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔄 Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

Set-Location app
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload