# ==============================================================================
# Sharpening CORTEX - Reset All Applications
# ==============================================================================
# Purpose: Quick reset script for all sample applications
# Usage: .\reset-all.ps1
# Location: sharpening-cortex/reset-all.ps1
# ==============================================================================

Write-Host "🔄 Resetting all Sharpening CORTEX applications..." -ForegroundColor Cyan

$ErrorActionPreference = "Continue"
$StartTime = Get-Date

# -------------------------------------------------------------------------
# 1. BadMonolith (SQL Seed)
# -------------------------------------------------------------------------
Write-Host "`n[1/5] Resetting BadMonolith..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/tasks?action=seed" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✅ BadMonolith reset successful" -ForegroundColor Green
        $BadMonolithSuccess = $true
    }
} catch {
    Write-Host "  ⚠️ BadMonolith reset failed: $_" -ForegroundColor Red
    $BadMonolithSuccess = $false
}

# -------------------------------------------------------------------------
# 2. CleanSolidApp (EF Migration)
# -------------------------------------------------------------------------
Write-Host "`n[2/5] Resetting CleanSolidApp..." -ForegroundColor Yellow
try {
    Push-Location "$PSScriptRoot\CleanSolidApp\backend"
    
    # Drop database
    dotnet ef database drop --force 2>&1 | Out-Null
    
    # Recreate with migrations
    dotnet ef database update 2>&1 | Out-Null
    
    # Seed data
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/tasks/seed" -Method GET -TimeoutSec 10
    
    Pop-Location
    Write-Host "  ✅ CleanSolidApp reset successful" -ForegroundColor Green
    $CleanSolidAppSuccess = $true
} catch {
    Pop-Location
    Write-Host "  ⚠️ CleanSolidApp reset failed: $_" -ForegroundColor Red
    $CleanSolidAppSuccess = $false
}

# -------------------------------------------------------------------------
# 3. _Real (Git Checkout)
# -------------------------------------------------------------------------
Write-Host "`n[3/5] Resetting _Real applications..." -ForegroundColor Yellow
try {
    Push-Location "$PSScriptRoot\_Real"
    
    # Hard reset to HEAD
    git checkout HEAD -- . 2>&1 | Out-Null
    
    # Verify clean
    $status = git status --porcelain
    
    Pop-Location
    
    if ($status.Length -eq 0) {
        Write-Host "  ✅ _Real reset successful (git clean)" -ForegroundColor Green
        $RealSuccess = $true
    } else {
        Write-Host "  ⚠️ _Real has uncommitted changes" -ForegroundColor Yellow
        $RealSuccess = $false
    }
} catch {
    Pop-Location
    Write-Host "  ⚠️ _Real reset failed: $_" -ForegroundColor Red
    $RealSuccess = $false
}

# -------------------------------------------------------------------------
# 4. Cortex-Clean (Docker Compose)
# -------------------------------------------------------------------------
Write-Host "`n[4/5] Resetting Cortex-Clean..." -ForegroundColor Yellow
try {
    Push-Location "$PSScriptRoot\Cortex-Clean"
    
    # Stop and remove containers + volumes
    docker-compose down -v 2>&1 | Out-Null
    
    # Start fresh
    docker-compose up -d 2>&1 | Out-Null
    
    # Wait for health check
    Start-Sleep -Seconds 5
    
    Pop-Location
    Write-Host "  ✅ Cortex-Clean reset successful" -ForegroundColor Green
    $CortexCleanSuccess = $true
} catch {
    Pop-Location
    Write-Host "  ⚠️ Cortex-Clean reset failed: $_" -ForegroundColor Red
    $CortexCleanSuccess = $false
}

# -------------------------------------------------------------------------
# 5. Cortex-SDD (Test Fixtures)
# -------------------------------------------------------------------------
Write-Host "`n[5/5] Resetting Cortex-SDD..." -ForegroundColor Yellow
try {
    Push-Location "$PSScriptRoot\Cortex-SDD"
    
    # Clear pytest cache
    if (Test-Path ".pytest_cache") {
        Remove-Item -Recurse -Force ".pytest_cache" 2>&1 | Out-Null
    }
    
    # Run fixture reset
    pytest --fixtures-reset 2>&1 | Out-Null
    
    Pop-Location
    Write-Host "  ✅ Cortex-SDD reset successful" -ForegroundColor Green
    $CortexSDDSuccess = $true
} catch {
    Pop-Location
    Write-Host "  ⚠️ Cortex-SDD reset failed: $_" -ForegroundColor Red
    $CortexSDDSuccess = $false
}

# -------------------------------------------------------------------------
# Summary Report
# -------------------------------------------------------------------------
$EndTime = Get-Date
$Duration = ($EndTime - $StartTime).TotalSeconds

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "RESET SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

$SuccessCount = 0
$SuccessCount += if ($BadMonolithSuccess) { 1 } else { 0 }
$SuccessCount += if ($CleanSolidAppSuccess) { 1 } else { 0 }
$SuccessCount += if ($RealSuccess) { 1 } else { 0 }
$SuccessCount += if ($CortexCleanSuccess) { 1 } else { 0 }
$SuccessCount += if ($CortexSDDSuccess) { 1 } else { 0 }

Write-Host "Total Applications: 5" -ForegroundColor White
Write-Host "Successful Resets:  $SuccessCount" -ForegroundColor $(if ($SuccessCount -eq 5) { "Green" } else { "Yellow" })
Write-Host "Failed Resets:      $(5 - $SuccessCount)" -ForegroundColor $(if ($SuccessCount -eq 5) { "Green" } else { "Red" })
Write-Host "Execution Time:     $([math]::Round($Duration, 2)) seconds" -ForegroundColor White

Write-Host "`nApplication Status:" -ForegroundColor White
Write-Host "  BadMonolith:     $(if ($BadMonolithSuccess) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "  CleanSolidApp:   $(if ($CleanSolidAppSuccess) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "  _Real:           $(if ($RealSuccess) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "  Cortex-Clean:    $(if ($CortexCleanSuccess) { '✅' } else { '❌' })" -ForegroundColor White
Write-Host "  Cortex-SDD:      $(if ($CortexSDDSuccess) { '✅' } else { '❌' })" -ForegroundColor White

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan

if ($SuccessCount -eq 5) {
    Write-Host "🎉 All applications successfully reset to baseline!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  Some applications failed to reset. Check logs above." -ForegroundColor Yellow
    exit 1
}
