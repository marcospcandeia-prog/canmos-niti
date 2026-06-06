# Script PowerShell para iniciar CANMOS-NITI no Windows

Write-Host "CANMOS-NITI - Initialization Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "Checking Docker..." -ForegroundColor Yellow
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker found: $(docker --version)" -ForegroundColor Green

# Check Docker Compose
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker Compose not found." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker Compose found" -ForegroundColor Green

# Check .env
if (!(Test-Path ".env")) {
    Write-Host "ERROR: .env file not found." -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure it." -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ .env file found" -ForegroundColor Green

Write-Host ""
Write-Host "Starting Docker containers..." -ForegroundColor Yellow
docker compose up -d

Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Checking services status..." -ForegroundColor Yellow
docker compose ps

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "CANMOS-NITI Started Successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services available at:" -ForegroundColor Yellow
Write-Host "  Frontend:        http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:     http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs:        http://localhost:8000/docs" -ForegroundColor White
Write-Host "  MinIO Console:   http://localhost:9001" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Download Ollama model: docker exec canmos-ollama ollama pull phi3:mini" -ForegroundColor White
Write-Host "  2. Run migrations: cd backend && alembic upgrade head" -ForegroundColor White
Write-Host "  3. Access frontend at http://localhost:3000" -ForegroundColor White
Write-Host ""
