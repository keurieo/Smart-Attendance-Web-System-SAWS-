# Smart Attendance System - Docker Starter and Test Runner
# This script starts Docker Desktop and runs tests

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Docker Desktop Starter" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker Desktop is installed
$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
if (-not (Test-Path $dockerPath)) {
    Write-Host "✗ Docker Desktop is not installed at the default location" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative locations to check:" -ForegroundColor Yellow
    Write-Host "  - C:\Program Files\Docker\Docker\Docker Desktop.exe" -ForegroundColor Gray
    Write-Host "  - C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe" -ForegroundColor Gray
    exit 1
}

Write-Host "✓ Docker Desktop found" -ForegroundColor Green

# Check if Docker is already running
Write-Host "Checking if Docker is already running..." -ForegroundColor Yellow
try {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker is already running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Proceeding to run tests..." -ForegroundColor Cyan
        Write-Host ""
        & ".\run-tests.ps1"
        exit 0
    }
} catch {
    # Docker not running, continue to start it
}

Write-Host "Docker is not running. Starting Docker Desktop..." -ForegroundColor Yellow
Write-Host ""

# Start Docker Desktop
try {
    Start-Process $dockerPath -ErrorAction Stop
    Write-Host "✓ Docker Desktop starting..." -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to start Docker Desktop" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Waiting for Docker to initialize..." -ForegroundColor Yellow
Write-Host "This may take 30-60 seconds..." -ForegroundColor Gray
Write-Host ""

# Wait for Docker to be ready (max 2 minutes)
$maxAttempts = 24  # 24 * 5 seconds = 2 minutes
$attempt = 0
$dockerReady = $false

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "  Attempt $attempt/$maxAttempts..." -ForegroundColor Gray
    
    try {
        docker ps 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $dockerReady = $true
            break
        }
    } catch {
        # Docker not ready yet
    }
    
    Start-Sleep -Seconds 5
}

Write-Host ""

if ($dockerReady) {
    Write-Host "==================================" -ForegroundColor Green
    Write-Host "✓ Docker is Ready!" -ForegroundColor Green
    Write-Host "==================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now running tests..." -ForegroundColor Cyan
    Write-Host ""
    
    # Run the test script
    & ".\run-tests.ps1"
} else {
    Write-Host "==================================" -ForegroundColor Red
    Write-Host "✗ Docker Failed to Start" -ForegroundColor Red
    Write-Host "==================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Docker Desktop did not become ready within 2 minutes." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please try the following:" -ForegroundColor Yellow
    Write-Host "1. Check if Docker Desktop window opened" -ForegroundColor White
    Write-Host "2. Wait for Docker Desktop to show 'Docker Desktop is running'" -ForegroundColor White
    Write-Host "3. Then manually run: .\run-tests.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "- Virtualization not enabled in BIOS" -ForegroundColor Gray
    Write-Host "- WSL 2 not installed (required for Docker on Windows)" -ForegroundColor Gray
    Write-Host "- Insufficient system resources" -ForegroundColor Gray
    Write-Host ""
    exit 1
}
