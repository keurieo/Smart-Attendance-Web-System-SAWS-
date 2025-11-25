# Smart Attendance System - Docker Startup Script
# This script starts all Docker containers and sets up the application

Write-Host "🚀 Starting Smart Attendance System..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Start all containers
Write-Host ""
Write-Host "📦 Starting Docker containers..." -ForegroundColor Cyan
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to start containers" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Check container status
Write-Host ""
Write-Host "📊 Container Status:" -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "✅ Smart Attendance System is running!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access the application at:" -ForegroundColor Cyan
Write-Host "   Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API:  http://localhost:8000/api" -ForegroundColor White
Write-Host "   Django Admin: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Default Login Credentials:" -ForegroundColor Cyan
Write-Host "   Email:    admin@example.com" -ForegroundColor White
Write-Host "   Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "📝 Useful Commands:" -ForegroundColor Cyan
Write-Host "   Stop:     docker-compose down" -ForegroundColor White
Write-Host "   Logs:     docker-compose logs -f [service_name]" -ForegroundColor White
Write-Host "   Restart:  docker-compose restart [service_name]" -ForegroundColor White
Write-Host ""
