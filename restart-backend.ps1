# Restart Backend Services Script
# This script restarts Django backend services and verifies startup

Write-Host "=== Backend Service Restart Script ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
$dockerAvailable = $false
try {
    docker --version | Out-Null
    $dockerAvailable = $true
    Write-Host "[OK] Docker is available" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Docker is not available or not running" -ForegroundColor Yellow
}

Write-Host ""

if ($dockerAvailable) {
    Write-Host "Checking Docker containers..." -ForegroundColor Cyan
    
    # Check if backend container exists
    $backendContainer = docker ps -a --filter "name=attendance_backend" --format "{{.Names}}"
    
    if ($backendContainer) {
        Write-Host "[OK] Found backend container: $backendContainer" -ForegroundColor Green
        Write-Host ""
        Write-Host "Restarting backend container..." -ForegroundColor Cyan
        docker-compose restart backend
        
        Write-Host ""
        Write-Host "Waiting for backend to start..." -ForegroundColor Cyan
        Start-Sleep -Seconds 5
        
        Write-Host ""
        Write-Host "Checking backend logs (last 20 lines):" -ForegroundColor Cyan
        docker-compose logs --tail=20 backend
        
        Write-Host ""
        Write-Host "[OK] Backend container restarted" -ForegroundColor Green
        Write-Host ""
        Write-Host "To view live logs, run: docker-compose logs -f backend" -ForegroundColor Yellow
    } else {
        Write-Host "[WARN] Backend container not found" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "To start all services, run: docker-compose up -d" -ForegroundColor Yellow
        Write-Host "Or use the start-docker.ps1 script" -ForegroundColor Yellow
    }
} else {
    Write-Host "Docker is not running. Checking for local Django server..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To start Django development server locally:" -ForegroundColor Yellow
    Write-Host "  1. cd backend" -ForegroundColor White
    Write-Host "  2. python manage.py runserver" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Make sure your virtual environment is activated and dependencies are installed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Restart Complete ===" -ForegroundColor Cyan
