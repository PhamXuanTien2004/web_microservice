# PowerShell Script - Start all services for E2E testing
# Usage: .\START_ALL.ps1

$workspace = "e:\TIEN_TT\web_microservice"

function Start-Service {
    param([string]$ServiceName, [string]$ServicePath, [string]$Command)
    
    Write-Host "`n==== Starting: $ServiceName ====" -ForegroundColor Cyan
    Start-Process -NoNewWindow -WorkingDirectory $ServicePath -FilePath "cmd.exe" -ArgumentList "/c $Command"
    Write-Host "[OK] $ServiceName started" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

# Note: Make sure MySQL is running separately
Write-Host "`n[WARN] Make sure MySQL is running in background" -ForegroundColor Yellow
Write-Host "       Services require MySQL on localhost:3306" -ForegroundColor Gray

# Start Services
Write-Host "`n[LAUNCH] Starting services..." -ForegroundColor Cyan

Start-Service -ServiceName "Auth Service (5001)" -ServicePath "$workspace\backend\auth-service" -Command "python run.py"
Start-Service -ServiceName "User Service (5002)" -ServicePath "$workspace\backend\user-service" -Command "python run.py"
Start-Service -ServiceName "Gateway Service (5000)" -ServicePath "$workspace\backend\gateway-service" -Command "python run.py"

Write-Host "`n[WEB] Starting frontend..." -ForegroundColor Cyan
Start-Process -NoNewWindow -WorkingDirectory "$workspace\frontend" -FilePath "cmd.exe" -ArgumentList "/c npm run dev"
Write-Host "[OK] Frontend started (port 5173)" -ForegroundColor Green

# Summary
Write-Host "`n==== All Services Running ====" -ForegroundColor Green
Write-Host "Auth Service:   http://localhost:5001/" -ForegroundColor Cyan
Write-Host "User Service:   http://localhost:5002/" -ForegroundColor Cyan
Write-Host "Gateway:        http://localhost:5000/" -ForegroundColor Cyan
Write-Host "Frontend:       http://localhost:5173/" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Green
Write-Host "Next: Open http://localhost:5173 in your browser" -ForegroundColor Yellow

Write-Host "`n[WAIT] Initializing..." -ForegroundColor Gray
for ($i = 30; $i -gt 0; $i--) {
    Write-Host -NoNewline "`r[$i] seconds"
    Start-Sleep -Seconds 1
}
Write-Host "`n[OK] Ready to test!" -ForegroundColor Green
