# Smart Attendance System - Test Runner Script
# This script helps run tests using Docker

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Smart Attendance System - Test Runner" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker command failed"
    }
    Write-Host "✓ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check if Docker daemon is running
Write-Host "Checking if Docker daemon is running..." -ForegroundColor Yellow
try {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker daemon not running"
    }
    Write-Host "✓ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and wait for it to fully initialize" -ForegroundColor Yellow
    Write-Host "Then run this script again" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Building Docker Containers" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Build containers
Write-Host "Building backend container (this may take a few minutes)..." -ForegroundColor Yellow
docker-compose build backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to build backend container" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Backend container built successfully" -ForegroundColor Green

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Starting Services" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Start services
Write-Host "Starting database and Redis..." -ForegroundColor Yellow
docker-compose up -d db redis
Start-Sleep -Seconds 10  # Wait for services to be ready

Write-Host "Starting backend..." -ForegroundColor Yellow
docker-compose up -d backend
Start-Sleep -Seconds 5

Write-Host "✓ Services started" -ForegroundColor Green

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Running Database Migrations" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Run migrations
Write-Host "Applying database migrations..." -ForegroundColor Yellow
docker-compose exec -T backend python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Migrations failed" -ForegroundColor Red
    Write-Host "Check the error above for details" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Migrations completed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Running Tests" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Run tests
Write-Host "Executing pytest..." -ForegroundColor Yellow
docker-compose exec -T backend python -m pytest -v --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "✓ All Tests Passed!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "==================================" -ForegroundColor Red
    Write-Host "✗ Some Tests Failed" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Red
    Write-Host "Review the output above for details" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Service URLs" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000/api" -ForegroundColor White
Write-Host "Admin Panel: http://localhost:8000/admin" -ForegroundColor White
Write-Host "Health Check: http://localhost:8000/api/health/" -ForegroundColor White
Write-Host ""
Write-Host "To stop services: docker-compose down" -ForegroundColor Yellow
Write-Host "To view logs: docker-compose logs -f backend" -ForegroundColor Yellow
Write-Host ""
