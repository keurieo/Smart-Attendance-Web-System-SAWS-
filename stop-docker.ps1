# Smart Attendance System - Docker Stop Script
# This script stops all Docker containers

Write-Host "🛑 Stopping Smart Attendance System..." -ForegroundColor Cyan
Write-Host ""

# Stop all containers
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All containers stopped successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Failed to stop containers" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "💡 To start again, run: .\start-docker.ps1" -ForegroundColor Cyan
Write-Host ""
