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

# Auto-detect CORTEX root by searching upward for cortex-brain/ marker
$ScriptPath = $PSCommandPath
if (-not $ScriptPath) {
    $ScriptPath = $MyInvocation.MyCommand.Path
}

function Find-CortexRoot {
    param([string]$StartPath)
    
    $CurrentDir = $PWD.Path
    $ScriptDir = if ($StartPath) { Split-Path -Parent $StartPath } else { $CurrentDir }
    
    # Try script directory first
    $TestDir = $ScriptDir
    while ($TestDir) {
        $MarkerPath = Join-Path $TestDir "cortex-brain"
        if (Test-Path $MarkerPath) {
            return $TestDir
        }
        $Parent = Split-Path -Parent $TestDir
        if ($Parent -eq $TestDir) { break }
        $TestDir = $Parent
    }
    
    # Try current directory
    $TestDir = $CurrentDir
    while ($TestDir) {
        $MarkerPath = Join-Path $TestDir "cortex-brain"
        if (Test-Path $MarkerPath) {
            return $TestDir
        }
        $Parent = Split-Path -Parent $TestDir
        if ($Parent -eq $TestDir) { break }
        $TestDir = $Parent
    }
    
    return $null
}

$CortexRoot = Find-CortexRoot -StartPath $ScriptPath
if (-not $CortexRoot) {
    Write-Host "ERROR: Cannot locate CORTEX root directory!" -ForegroundColor $ErrorColor
    Write-Host "Please run this script from within the CORTEX repository." -ForegroundColor $ErrorColor
    exit 1
}

$DashboardDir = Join-Path $CortexRoot "cortex-brain" | Join-Path -ChildPath "dashboards"

Write-Host "`n========================================================" -ForegroundColor $InfoColor
Write-Host "       CORTEX DASHBOARD LAUNCHER v1.1.0                " -ForegroundColor $InfoColor
Write-Host "========================================================`n" -ForegroundColor $InfoColor

# Kill all running Python HTTP servers
Write-Host "Cleaning up existing Python processes..." -ForegroundColor $InfoColor
try {
    $PythonProcesses = Get-Process -Name python*, py -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*http.server*" -or $_.Path -like "*python*" }
    
    if ($PythonProcesses) {
        $Count = ($PythonProcesses | Measure-Object).Count
        Write-Host "Found $Count Python process(es) running" -ForegroundColor $WarningColor
        $PythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
        Write-Host "Cleaned up Python processes" -ForegroundColor $SuccessColor
    } else {
        Write-Host "No existing Python processes found" -ForegroundColor $SuccessColor
    }
}
catch {
    Write-Host "Could not clean up processes (may require admin rights)" -ForegroundColor $WarningColor
}
Write-Host ""

# Validate dashboard directory exists
if (-not (Test-Path $DashboardDir)) {
    Write-Host "ERROR: Dashboard directory not found!" -ForegroundColor $ErrorColor
    Write-Host "Expected: $DashboardDir" -ForegroundColor $ErrorColor
    Write-Host "CORTEX Root: $CortexRoot" -ForegroundColor $WarningColor
    exit 1
}

# Validate ui/ subdirectory exists
$UiDir = Join-Path $DashboardDir "ui"
if (-not (Test-Path $UiDir)) {
    Write-Host "ERROR: Dashboard UI directory not found!" -ForegroundColor $ErrorColor
    Write-Host "Expected: $UiDir" -ForegroundColor $ErrorColor
    exit 1
}

# Check if port is already in use (cross-platform)
function Test-PortInUse {
    param([int]$PortNumber)
    
    try {
        # Try Windows-specific method first
        if ($IsWindows -or (-not (Get-Variable IsWindows -ErrorAction SilentlyContinue))) {
            $Connection = Get-NetTCPConnection -LocalPort $PortNumber -ErrorAction SilentlyContinue
            return ($null -ne $Connection)
        }
        
        # Unix-like systems: try to bind to port
        $Listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $PortNumber)
        $Listener.Start()
        $Listener.Stop()
        return $false
    }
    catch {
        return $true
    }
}

if (Test-PortInUse -PortNumber $Port) {
    Write-Host "WARNING: Port $Port is already in use!" -ForegroundColor $WarningColor
    Write-Host "Attempting to use next available port..." -ForegroundColor $WarningColor
    
    # Try ports 8081-8089
    $PortFound = $false
    for ($i = 8081; $i -le 8089; $i++) {
        if (-not (Test-PortInUse -PortNumber $i)) {
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

# Detect Python executable (cross-platform)
$PythonCmd = $null
$PythonCandidates = @("python", "python3", "py")
foreach ($Cmd in $PythonCandidates) {
    try {
        $TestResult = & $Cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PythonCmd = $Cmd
            Write-Host "Using Python: " -NoNewline
            Write-Host $Cmd -ForegroundColor $SuccessColor
            break
        }
    }
    catch {
        continue
    }
}

if (-not $PythonCmd) {
    Write-Host "ERROR: Python not found!" -ForegroundColor $ErrorColor
    Write-Host "Please install Python 3.8+ and ensure it's in your PATH." -ForegroundColor $ErrorColor
    exit 1
}

# Start server
Write-Host "Starting HTTP server..." -ForegroundColor $InfoColor
Write-Host "Press Ctrl+C to stop server" -ForegroundColor $WarningColor
Write-Host ""
Write-Host "========================================================" -ForegroundColor $InfoColor
Write-Host ""

try {
    Set-Location $DashboardDir
    & $PythonCmd -m http.server $Port
}
catch {
    Write-Host ""
    Write-Host "ERROR: Failed to start server!" -ForegroundColor $ErrorColor
    Write-Host $_.Exception.Message -ForegroundColor $ErrorColor
    exit 1
}
finally {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor $InfoColor
    Write-Host "Server stopped." -ForegroundColor $SuccessColor
    Set-Location $CortexRoot
}
