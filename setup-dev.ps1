# Smart Attendance System - Development Environment Setup Script
# This script automates the setup process for Windows development environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Smart Attendance System - Dev Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        if (Get-Command $Command -ErrorAction Stop) {
            return $true
        }
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
if (Test-Command python) {
    $pythonVersion = python --version
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Docker
if (Test-Command docker) {
    $dockerVersion = docker --version
    Write-Host "✓ Docker installed: $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check if Docker is running
Write-Host ""
Write-Host "Checking if Docker Desktop is running..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "  Please start Docker Desktop and run this script again" -ForegroundColor Yellow
    exit 1
}

# Check virtual environment
Write-Host ""
Write-Host "Checking Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "backend\venv") {
    Write-Host "✓ Virtual environment exists" -ForegroundColor Green
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv backend\venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Check environment files
Write-Host ""
Write-Host "Checking environment files..." -ForegroundColor Yellow

if (!(Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✓ Created backend\.env" -ForegroundColor Green
} else {
    Write-Host "✓ backend\.env exists" -ForegroundColor Green
}

if (!(Test-Path "frontend\.env")) {
    Copy-Item "frontend\.env.example" "frontend\.env"
    Write-Host "✓ Created frontend\.env" -ForegroundColor Green
} else {
    Write-Host "✓ frontend\.env exists" -ForegroundColor Green
}

# Start Docker services
Write-Host ""
Write-Host "Starting Docker services (PostgreSQL + Redis)..." -ForegroundColor Yellow
docker-compose up -d db redis

Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if services are running
$dbStatus = docker-compose ps db --format json | ConvertFrom-Json
$redisStatus = docker-compose ps redis --format json | ConvertFrom-Json

if ($dbStatus.State -eq "running") {
    Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "✗ PostgreSQL failed to start" -ForegroundColor Red
}

if ($redisStatus.State -eq "running") {
    Write-Host "✓ Redis is running" -ForegroundColor Green
} else {
    Write-Host "✗ Redis failed to start" -ForegroundColor Red
}

# Run migrations
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Yellow
& backend\venv\Scripts\python.exe backend\manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migrations completed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Migrations failed" -ForegroundColor Red
    Write-Host "  Check the error messages above" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services Status:" -ForegroundColor Yellow
Write-Host "  PostgreSQL: http://localhost:5432" -ForegroundColor White
Write-Host "  Redis: http://localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Create superuser:" -ForegroundColor White
Write-Host "     backend\venv\Scripts\activate" -ForegroundColor Gray
Write-Host "     python backend\manage.py createsuperuser" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start development server:" -ForegroundColor White
Write-Host "     python backend\manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Access the application:" -ForegroundColor White
Write-Host "     Admin: http://localhost:8000/admin" -ForegroundColor Gray
Write-Host "     API: http://localhost:8000/api" -ForegroundColor Gray
Write-Host ""
Write-Host "For more details, see ENVIRONMENT_SETUP_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
