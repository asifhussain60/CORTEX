#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Launch CORTEX Dashboard Server

.DESCRIPTION
    Starts HTTP server from correct directory (cortex-brain/dashboards/)
    and opens dashboard in default browser.

.PARAMETER Port
    Port number to use (default: 8080)

.PARAMETER NoBrowser
    Skip opening browser automatically

.EXAMPLE
    .\launch-dashboard.ps1
    
.EXAMPLE
    .\launch-dashboard.ps1 -Port 9000
    
.EXAMPLE
    .\launch-dashboard.ps1 -NoBrowser

.NOTES
    Author: Asif Hussain
    Copyright: © 2024-2025 Asif Hussain. All rights reserved.
    Version: 1.0.0
#>

param(
    [int]$Port = 8080,
    [switch]$NoBrowser
)

# Colors
$InfoColor = "Cyan"
$SuccessColor = "Green"
$ErrorColor = "Red"
$WarningColor = "Yellow"

# Get script directory (CORTEX root)
$CortexRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DashboardDir = Join-Path $CortexRoot "cortex-brain\dashboards"

Write-Host "`n╔════════════════════════════════════════════════════════╗" -ForegroundColor $InfoColor
Write-Host "║          CORTEX DASHBOARD LAUNCHER v1.0.0            ║" -ForegroundColor $InfoColor
Write-Host "╚════════════════════════════════════════════════════════╝`n" -ForegroundColor $InfoColor

# Validate dashboard directory exists
if (-not (Test-Path $DashboardDir)) {
    Write-Host "ERROR: Dashboard directory not found!" -ForegroundColor $ErrorColor
    Write-Host "Expected: $DashboardDir" -ForegroundColor $ErrorColor
    exit 1
}

# Validate ui/ subdirectory exists
$UiDir = Join-Path $DashboardDir "ui"
if (-not (Test-Path $UiDir)) {
    Write-Host "ERROR: Dashboard UI directory not found!" -ForegroundColor $ErrorColor
    Write-Host "Expected: $UiDir" -ForegroundColor $ErrorColor
    exit 1
}

# Check if port is already in use
$PortInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($PortInUse) {
    Write-Host "WARNING: Port $Port is already in use!" -ForegroundColor $WarningColor
    Write-Host "Attempting to use next available port..." -ForegroundColor $WarningColor
    
    # Try ports 8081-8089
    $PortFound = $false
    for ($i = 8081; $i -le 8089; $i++) {
        $TestPort = Get-NetTCPConnection -LocalPort $i -ErrorAction SilentlyContinue
        if (-not $TestPort) {
            $Port = $i
            $PortFound = $true
            Write-Host "Using port $Port instead" -ForegroundColor $SuccessColor
            break
        }
    }
    
    if (-not $PortFound) {
        Write-Host "ERROR: All ports 8080-8089 are in use!" -ForegroundColor $ErrorColor
        Write-Host "Please stop other services or specify a different port." -ForegroundColor $ErrorColor
        exit 1
    }
}

# Display configuration
Write-Host "Configuration:" -ForegroundColor $InfoColor
Write-Host "  Dashboard Directory: " -NoNewline
Write-Host $DashboardDir -ForegroundColor $SuccessColor
Write-Host "  Port: " -NoNewline
Write-Host $Port -ForegroundColor $SuccessColor
Write-Host "  URL: " -NoNewline
Write-Host "http://localhost:$Port/ui/index.html?source=mock" -ForegroundColor $SuccessColor
Write-Host ""

# Open browser if requested
if (-not $NoBrowser) {
    Write-Host "Opening dashboard in browser..." -ForegroundColor $InfoColor
    Start-Sleep -Seconds 2  # Give server time to start
    Start-Process "http://localhost:$Port/ui/index.html?source=mock"
}

# Start server
Write-Host "Starting HTTP server..." -ForegroundColor $InfoColor
Write-Host "Press Ctrl+C to stop server`n" -ForegroundColor $WarningColor
Write-Host "════════════════════════════════════════════════════════`n" -ForegroundColor $InfoColor

try {
    Set-Location $DashboardDir
    python -m http.server $Port
}
catch {
    Write-Host "`nERROR: Failed to start server!" -ForegroundColor $ErrorColor
    Write-Host $_.Exception.Message -ForegroundColor $ErrorColor
    exit 1
}
finally {
    Write-Host "`n════════════════════════════════════════════════════════" -ForegroundColor $InfoColor
    Write-Host "Server stopped." -ForegroundColor $SuccessColor
    Set-Location $CortexRoot
}
