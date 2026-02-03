# PowerShell Script - Start all services for E2E testing
# Usage: .\START_SERVICES.ps1

$workspace = "e:\TIEN_TT\web_microservice"
$projectPath = $workspace

function Start-Service {
    param(
        [string]$ServiceName,
        [string]$ServicePath,
        [string]$Command
    )
    
    Write-Host "`n==== Starting: $ServiceName ====" -ForegroundColor Cyan
    Write-Host "Path: $ServicePath" -ForegroundColor Gray
    
    Start-Process -NoNewWindow -WorkingDirectory $ServicePath -FilePath "cmd.exe" -ArgumentList "/c $Command"
    
    Write-Host "[OK] $ServiceName started in background" -ForegroundColor Green
    Start-Sleep -Seconds 3
}

# Step 1: Check MySQL is running
Write-Host "`n[CHECK] Checking MySQL connection..." -ForegroundColor Yellow
try {
    $result = mysql -u auth_user -proot@root -e "SELECT 1;" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] MySQL is running and accessible" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] MySQL not accessible. Please start MySQL service first." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] MySQL not found. Please start MySQL service first." -ForegroundColor Red
    exit 1
}

# Step 2: Start Backend Services
Write-Host "`n[LAUNCH] Starting backend services..." -ForegroundColor Cyan

$authServicePath = "$projectPath\backend\auth-service"
$userServicePath = "$projectPath\backend\user-service"
$gatewayPath = "$projectPath\backend\gateway-service"

# Terminal 1: Auth Service (port 5001)
Start-Service -ServiceName "Auth Service (5001)" -ServicePath $authServicePath -Command "python run.py"

# Terminal 2: User Service (port 5002)
Start-Service -ServiceName "User Service (5002)" -ServicePath $userServicePath -Command "python run.py"

# Terminal 3: Gateway Service (port 5000)
Start-Service -ServiceName "Gateway Service (5000)" -ServicePath $gatewayPath -Command "python run.py"

# Step 3: Start Frontend
Write-Host "`n[WEB] Starting frontend dev server..." -ForegroundColor Cyan
$frontendPath = "$projectPath\frontend"
Start-Process -NoNewWindow -WorkingDirectory $frontendPath -FilePath "cmd.exe" -ArgumentList "/c npm run dev"
Write-Host "[OK] Frontend started in background (port 5173)" -ForegroundColor Green

# Step 4: Summary
Write-Host "`n==== All services launched! ====" -ForegroundColor Green
Write-Host "Services running on:" -ForegroundColor Green
Write-Host "  * Auth Service:    http://localhost:5001/" -ForegroundColor Cyan
Write-Host "  * User Service:    http://localhost:5002/" -ForegroundColor Cyan
Write-Host "  * Gateway:         http://localhost:5000/" -ForegroundColor Cyan
Write-Host "  * Frontend:        http://localhost:5173/" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "  1. Check backend terminal windows for errors" -ForegroundColor Yellow
Write-Host "  2. Open http://localhost:5173 in your browser" -ForegroundColor Yellow
Write-Host "  3. Test login/register flow" -ForegroundColor Yellow
Write-Host "  4. Check DevTools (F12) - Network tab" -ForegroundColor Yellow
Write-Host "  5. Look for Set-Cookie headers on login response" -ForegroundColor Yellow
Write-Host "  6. Look for Cookie headers on profile request" -ForegroundColor Yellow
Write-Host "" -ForegroundColor Green
Write-Host "Debug tips:" -ForegroundColor Yellow
Write-Host "  * E2E_TEST.md has full checklist" -ForegroundColor Gray
Write-Host "  * Check all backend terminal windows for errors" -ForegroundColor Gray
Write-Host "  * If 401 on profile: cookie not sent (SameSite issue)" -ForegroundColor Gray
Write-Host "  * If 404: path mismatch (check gateway routes)" -ForegroundColor Gray
