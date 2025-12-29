#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Launch CORTEX Admin Dashboard

.DESCRIPTION
    Starts HTTP server from the cortex-brain/dashboards/ directory
    and opens the admin dashboard in the default browser.
    
    CRITICAL REQUIREMENTS:
    - Server MUST run from cortex-brain/dashboards/ directory (not project root)
    - Dashboard UI is at ui/index.html
    - Supports multiple data sources via ?source= parameter
    - Automatically finds available port (8080-8089)
    - Kills existing Python HTTP servers before starting

.PARAMETER Port
    Port number to use (default: 8080). Will auto-increment if port is busy.

.PARAMETER NoBrowser
    Skip opening browser automatically

.PARAMETER DataSource
    Data source to use: mock, cortex, noor-canvas, alist, ksessions (default: mock)

.EXAMPLE
    .\launch_dashboard.ps1
    # Launches with mock data on port 8080

.EXAMPLE
    .\launch_dashboard.ps1 -Port 9000 -DataSource cortex
    # Launches with CORTEX data on port 9000

.EXAMPLE
    .\launch_dashboard.ps1 -NoBrowser
    # Launches without opening browser

.NOTES
    Author: Asif Hussain
    Copyright: © 2024-2025 Asif Hussain. All rights reserved.
    Version: 2.0.0
    
    ARCHITECTURE:
    - Dashboard UI: cortex-brain/dashboards/ui/
    - Data sources: cortex-brain/dashboards/ui/data/{source}/
    - Server root: cortex-brain/dashboards/ (CRITICAL)
    - Access URL: http://localhost:{port}/ui/index.html?source={source}
    
    DATA SOURCES:
    - mock: Example/demo data
    - cortex: CORTEX repository metrics
    - noor-canvas: Noor Canvas app metrics
    - alist: Alist app metrics
    - ksessions: K-Sessions app metrics
    
    TROUBLESHOOTING:
    - 404 errors: Server running from wrong directory (must be dashboards/)
    - Port in use: Script auto-increments to next available port (8081-8089)
    - Python not found: Install Python 3.8+ and add to PATH
#>

param(
    [int]$Port = 8080,
    [switch]$NoBrowser,
    [ValidateSet('mock', 'cortex', 'noor-canvas', 'alist', 'ksessions')]
    [string]$DataSource = 'mock'
)

#region Colors
$InfoColor = "Cyan"
$SuccessColor = "Green"
$ErrorColor = "Red"
$WarningColor = "Yellow"
#endregion

#region CORTEX Root Detection
function Find-CortexRoot {
    param([string]$StartPath)
    
    $CurrentDir = $PWD.Path
    $ScriptDir = if ($StartPath) { Split-Path -Parent $StartPath } else { $CurrentDir }
    
    # Try current directory first (most reliable)
    $TestDir = $CurrentDir
    while ($TestDir) {
        $MarkerPath = Join-Path $TestDir "cortex-brain"
        $DashboardPath = Join-Path $MarkerPath "dashboards"
        if ((Test-Path $MarkerPath) -and (Test-Path $DashboardPath)) {
            return $TestDir
        }
        $Parent = Split-Path -Parent $TestDir
        if ($Parent -eq $TestDir) { break }
        $TestDir = $Parent
    }
    
    # Try script directory
    $TestDir = $ScriptDir
    while ($TestDir) {
        $MarkerPath = Join-Path $TestDir "cortex-brain"
        $DashboardPath = Join-Path $MarkerPath "dashboards"
        if ((Test-Path $MarkerPath) -and (Test-Path $DashboardPath)) {
            return $TestDir
        }
        $Parent = Split-Path -Parent $TestDir
        if ($Parent -eq $TestDir) { break }
        $TestDir = $Parent
    }
    
    return $null
}

$ScriptPath = $PSCommandPath
if (-not $ScriptPath) {
    $ScriptPath = $MyInvocation.MyCommand.Path
}

$CortexRoot = Find-CortexRoot -StartPath $ScriptPath
if (-not $CortexRoot) {
    Write-Host "`nERROR: Cannot locate CORTEX root directory!" -ForegroundColor $ErrorColor
    Write-Host "Please run this script from within the CORTEX repository." -ForegroundColor $ErrorColor
    Write-Host "Expected structure: CORTEX/cortex-brain/dashboards/`n" -ForegroundColor $WarningColor
    exit 1
}
#endregion

#region Path Validation
$DashboardDir = Join-Path $CortexRoot "cortex-brain" | Join-Path -ChildPath "dashboards"
$UiDir = Join-Path $DashboardDir "ui"
$DataDir = Join-Path $UiDir "data"
$IndexHtml = Join-Path $UiDir "index.html"

Write-Host "`n============================================================" -ForegroundColor $InfoColor
Write-Host "         CORTEX ADMIN DASHBOARD LAUNCHER v2.0.0             " -ForegroundColor $InfoColor
Write-Host "============================================================`n" -ForegroundColor $InfoColor

# Validate dashboard directory structure
if (-not (Test-Path $DashboardDir)) {
    Write-Host "ERROR: Dashboard directory not found!" -ForegroundColor $ErrorColor
    Write-Host "Expected: $DashboardDir" -ForegroundColor $ErrorColor
    Write-Host "CORTEX Root: $CortexRoot`n" -ForegroundColor $WarningColor
    exit 1
}

if (-not (Test-Path $UiDir)) {
    Write-Host "ERROR: Dashboard UI directory not found!" -ForegroundColor $ErrorColor
    Write-Host "Expected: $UiDir" -ForegroundColor $ErrorColor
    Write-Host "The dashboard UI must be in cortex-brain/dashboards/ui/`n" -ForegroundColor $WarningColor
    exit 1
}

if (-not (Test-Path $IndexHtml)) {
    Write-Host "ERROR: Dashboard index.html not found!" -ForegroundColor $ErrorColor
    Write-Host "Expected: $IndexHtml" -ForegroundColor $ErrorColor
    Write-Host "The main dashboard file is missing.`n" -ForegroundColor $WarningColor
    exit 1
}

if (-not (Test-Path $DataDir)) {
    Write-Host "WARNING: Data directory not found!" -ForegroundColor $WarningColor
    Write-Host "Expected: $DataDir" -ForegroundColor $WarningColor
    Write-Host "Dashboard will start but may not have data to display.`n" -ForegroundColor $WarningColor
}
#endregion

#region Cleanup Existing Servers
Write-Host "Cleaning up existing Python HTTP servers..." -ForegroundColor $InfoColor
try {
    $PythonProcesses = Get-Process -Name python*, py -ErrorAction SilentlyContinue | 
        Where-Object { 
            $_.CommandLine -like "*http.server*" -or 
            $_.CommandLine -like "*SimpleHTTPServer*" 
        }
    
    if ($PythonProcesses) {
        $Count = ($PythonProcesses | Measure-Object).Count
        Write-Host "  Found $Count Python HTTP server(s) running" -ForegroundColor $WarningColor
        $PythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 500
        Write-Host "  ✓ Cleaned up existing servers" -ForegroundColor $SuccessColor
    } else {
        Write-Host "  ✓ No existing servers found" -ForegroundColor $SuccessColor
    }
}
catch {
    Write-Host "  ! Could not clean up processes (may require admin rights)" -ForegroundColor $WarningColor
}
Write-Host ""
#endregion

#region Port Detection
function Test-PortInUse {
    param([int]$PortNumber)
    
    try {
        # Windows-specific method
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

$OriginalPort = $Port
if (Test-PortInUse -PortNumber $Port) {
    Write-Host "WARNING: Port $Port is already in use!" -ForegroundColor $WarningColor
    Write-Host "Searching for available port..." -ForegroundColor $WarningColor
    
    # Try ports 8081-8089
    $PortFound = $false
    for ($i = ($Port + 1); $i -le 8089; $i++) {
        if (-not (Test-PortInUse -PortNumber $i)) {
            $Port = $i
            $PortFound = $true
            Write-Host "  ✓ Using port $Port instead" -ForegroundColor $SuccessColor
            break
        }
    }
    
    if (-not $PortFound) {
        Write-Host "`nERROR: All ports $OriginalPort-8089 are in use!" -ForegroundColor $ErrorColor
        Write-Host "Please stop other services or specify a different port.`n" -ForegroundColor $ErrorColor
        exit 1
    }
}
Write-Host ""
#endregion

#region Python Detection
$PythonCmd = $null
$PythonVersion = $null
$PythonCandidates = @("python", "python3", "py")

Write-Host "Detecting Python installation..." -ForegroundColor $InfoColor
foreach ($Cmd in $PythonCandidates) {
    try {
        $TestResult = & $Cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $PythonCmd = $Cmd
            $PythonVersion = $TestResult
            Write-Host "  ✓ Found Python: $PythonVersion" -ForegroundColor $SuccessColor
            break
        }
    }
    catch {
        continue
    }
}

if (-not $PythonCmd) {
    Write-Host "`nERROR: Python not found!" -ForegroundColor $ErrorColor
    Write-Host "Please install Python 3.8+ and ensure it's in your PATH." -ForegroundColor $ErrorColor
    Write-Host "Download from: https://www.python.org/downloads/`n" -ForegroundColor $WarningColor
    exit 1
}
Write-Host ""
#endregion

#region Dashboard Validation
Write-Host "Validating dashboard structure..." -ForegroundColor $InfoColor

# Define all required tabs and their components
$RequiredTabs = @(
    @{Name="Executive Summary"; Id="executive"; Container="executive-container"; Component="executive-tab.js"},
    @{Name="System Overview"; Id="overview"; Container="overview-container"; Component="overview-tab-v3.js"},
    @{Name="Tech Stack"; Id="tech-stack"; Container="tech-stack-container"; Component="tech-stack-tab.js"},
    @{Name="Security"; Id="security"; Container="security-container"; Component="security-tab.js"},
    @{Name="Use Cases"; Id="use-cases"; Container="use-cases-container"; Component="use-cases-tab.js"},
    @{Name="Recommendations"; Id="recommendations"; Container="recommendations-container"; Component="recommendations-tab.js"},
    @{Name="Architecture"; Id="architecture"; Container="architecture-container"; Component="architecture-tab.js"},
    @{Name="Code Organization"; Id="code-org"; Container="code-org-container"; Component="code-org-tab.js"},
    @{Name="Dependencies"; Id="vendors"; Container="vendors-container"; Component="vendors-tab.js"},
    @{Name="Onboarding"; Id="engineering"; Container="engineering-container"; Component="engineering-onboarding-tab.js"}
)

$ValidationErrors = @()
$ValidationWarnings = @()

# Check index.html exists and contains all tabs
$IndexContent = Get-Content $IndexHtml -Raw -ErrorAction SilentlyContinue
if ($IndexContent) {
    $TabsFound = 0
    $ComponentsFound = 0
    
    foreach ($Tab in $RequiredTabs) {
        # Check for nav tab definition
        $TabId = $Tab.Id
        $TabName = $Tab.Name
        $NavPattern = "data-tab=`"$TabId`""
        if ($IndexContent -match $NavPattern) {
            $TabsFound++
        } else {
            $ValidationErrors += "Missing nav tab: $TabName (data-tab=`"$TabId`")"
        }
        
        # Check for content container
        $TabContainer = $Tab.Container
        $ContainerPattern = "id=`"$TabContainer`""
        if ($IndexContent -match $ContainerPattern) {
            # Success - container exists
        } else {
            $ValidationWarnings += "Missing container: $TabContainer for tab $TabName"
        }
        
        # Check for component script
        $TabComponent = $Tab.Component
        $ComponentPattern = "src=`"components/$TabComponent`""
        if ($IndexContent -match $ComponentPattern) {
            $ComponentsFound++
        } else {
            $ValidationWarnings += "Missing component script: $TabComponent"
        }
    }
    
    $TabColor = if ($TabsFound -eq $RequiredTabs.Count) { $SuccessColor } else { $WarningColor }
    $ComponentColor = if ($ComponentsFound -eq $RequiredTabs.Count) { $SuccessColor } else { $WarningColor }
    $TotalTabs = $RequiredTabs.Count
    Write-Host "  ✓ Found $TabsFound/$TotalTabs nav tabs in index.html" -ForegroundColor $TabColor
    Write-Host "  ✓ Found $ComponentsFound/$TotalTabs component scripts" -ForegroundColor $ComponentColor
} else {
    $ValidationErrors += "Could not read index.html"
}

# Validate component files exist
$ComponentsDir = Join-Path $UiDir "components"
$MissingComponents = @()
foreach ($Tab in $RequiredTabs) {
    $ComponentPath = Join-Path $ComponentsDir $Tab.Component
    if (-not (Test-Path $ComponentPath)) {
        $MissingComponents += $Tab.Component
    }
}

if ($MissingComponents.Count -eq 0) {
    $TotalTabs = $RequiredTabs.Count
    Write-Host "  ✓ All $TotalTabs tab components exist" -ForegroundColor $SuccessColor
} else {
    $MissingCount = $MissingComponents.Count
    Write-Host "  ! Missing $MissingCount component files" -ForegroundColor $WarningColor
    $ValidationWarnings += $MissingComponents | ForEach-Object { "Missing component file: $_" }
}

# Check app.js for tab rendering
$AppJsPath = Join-Path $UiDir "app.js"
if (Test-Path $AppJsPath) {
    $AppJsContent = Get-Content $AppJsPath -Raw
    
    # Check for critical tab renders
    $CriticalRenders = @("renderUseCases", "renderRecommendations", "renderExecutiveSummary")
    $RendersFound = 0
    foreach ($Render in $CriticalRenders) {
        if ($AppJsContent -match $Render) {
            $RendersFound++
        }
    }
    
    $RenderColor = if ($RendersFound -eq $CriticalRenders.Count) { $SuccessColor } else { $WarningColor }
    $TotalRenders = $CriticalRenders.Count
    Write-Host "  ✓ Found $RendersFound/$TotalRenders critical render functions in app.js" -ForegroundColor $RenderColor
} else {
    $ValidationErrors += "app.js not found at $AppJsPath"
}

# Check switchTab function
if ($IndexContent -match "function switchTab") {
    Write-Host "  ✓ switchTab function found in index.html" -ForegroundColor $SuccessColor
} else {
    $ValidationWarnings += "switchTab function not found - tab switching may not work"
}

# Display validation results
Write-Host ""
if ($ValidationErrors.Count -gt 0) {
    $ErrorCount = $ValidationErrors.Count
    Write-Host "VALIDATION ERRORS ($ErrorCount):" -ForegroundColor $ErrorColor
    foreach ($Error in $ValidationErrors) {
        Write-Host "  ✗ $Error" -ForegroundColor $ErrorColor
    }
    Write-Host ""
    Write-Host "Dashboard structure is incomplete. Some features may not work." -ForegroundColor $ErrorColor
    Write-Host "Press Ctrl+C to cancel or any key to continue anyway..." -ForegroundColor $WarningColor
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Write-Host ""
}

if ($ValidationWarnings.Count -gt 0) {
    $WarningCount = $ValidationWarnings.Count
    Write-Host "VALIDATION WARNINGS ($WarningCount):" -ForegroundColor $WarningColor
    foreach ($Warning in $ValidationWarnings | Select-Object -First 5) {
        Write-Host "  ! $Warning" -ForegroundColor $WarningColor
    }
    if ($ValidationWarnings.Count -gt 5) {
        $MoreWarnings = $ValidationWarnings.Count - 5
        Write-Host "  ! ... and $MoreWarnings more warnings" -ForegroundColor $WarningColor
    }
    Write-Host ""
}

if ($ValidationErrors.Count -eq 0 -and $ValidationWarnings.Count -eq 0) {
    Write-Host "  ✓ Dashboard structure validation passed!" -ForegroundColor $SuccessColor
    Write-Host ""
}
#endregion

#region Configuration Display
$DashboardUrl = "http://localhost:$Port/ui/index.html?source=$DataSource"

Write-Host "Dashboard Configuration:" -ForegroundColor $InfoColor
Write-Host "  CORTEX Root      : " -NoNewline; Write-Host $CortexRoot -ForegroundColor $SuccessColor
Write-Host "  Dashboard Dir    : " -NoNewline; Write-Host $DashboardDir -ForegroundColor $SuccessColor
Write-Host "  UI Dir           : " -NoNewline; Write-Host $UiDir -ForegroundColor $SuccessColor
Write-Host "  Server Port      : " -NoNewline; Write-Host $Port -ForegroundColor $SuccessColor
Write-Host "  Data Source      : " -NoNewline; Write-Host $DataSource -ForegroundColor $SuccessColor
Write-Host "  Dashboard URL    : " -NoNewline; Write-Host $DashboardUrl -ForegroundColor $SuccessColor
$ValidatedCount = $RequiredTabs.Count
Write-Host "  Validated Tabs   : " -NoNewline; Write-Host "$ValidatedCount tabs configured" -ForegroundColor $SuccessColor
Write-Host ""

Write-Host "Available Data Sources:" -ForegroundColor $InfoColor
Write-Host "  • mock         - Example/demo data" -ForegroundColor Gray
Write-Host "  • cortex       - CORTEX repository metrics" -ForegroundColor Gray
Write-Host "  • noor-canvas  - Noor Canvas app metrics" -ForegroundColor Gray
Write-Host "  • alist        - Alist app metrics" -ForegroundColor Gray
Write-Host "  • ksessions    - K-Sessions app metrics" -ForegroundColor Gray
Write-Host ""

Write-Host "Dashboard Tabs:" -ForegroundColor $InfoColor
Write-Host "  📊 Executive Summary  🏠 System Overview   ⚙️  Tech Stack" -ForegroundColor Gray
Write-Host "  🔒 Security          🎯 Use Cases          💡 Recommendations" -ForegroundColor Gray
Write-Host "  🏗️  Architecture      📁 Code Organization  🔌 Dependencies" -ForegroundColor Gray
Write-Host "  🎓 Onboarding" -ForegroundColor Gray
Write-Host ""

Write-Host "Change data source by adding ?source={name} to URL" -ForegroundColor $WarningColor
Write-Host ""
#endregion

#region Browser Launch
if (-not $NoBrowser) {
    Write-Host "Opening dashboard in browser..." -ForegroundColor $InfoColor
    Start-Sleep -Milliseconds 1500  # Give server time to start
    
    try {
        Start-Process $DashboardUrl
        Write-Host "  ✓ Browser launched" -ForegroundColor $SuccessColor
    }
    catch {
        Write-Host "  ! Could not open browser automatically" -ForegroundColor $WarningColor
        Write-Host "  Please open manually: $DashboardUrl" -ForegroundColor $WarningColor
    }
    Write-Host ""
}
#endregion

#region Server Start
Write-Host "============================================================" -ForegroundColor $InfoColor
Write-Host "Starting HTTP server from: $DashboardDir" -ForegroundColor $InfoColor
Write-Host "============================================================" -ForegroundColor $InfoColor
Write-Host ""
Write-Host "Dashboard URL: " -NoNewline
Write-Host $DashboardUrl -ForegroundColor $SuccessColor
Write-Host ""
Write-Host "Press " -NoNewline
Write-Host "Ctrl+C" -ForegroundColor $WarningColor -NoNewline
Write-Host " to stop server"
Write-Host ""
Write-Host "============================================================" -ForegroundColor $InfoColor
Write-Host ""

try {
    # CRITICAL: Change to dashboard directory before starting server
    Push-Location $DashboardDir
    
    # Start Python HTTP server
    & $PythonCmd -m http.server $Port --bind 127.0.0.1
}
catch {
    Write-Host ""
    Write-Host "ERROR: Failed to start server!" -ForegroundColor $ErrorColor
    Write-Host $_.Exception.Message -ForegroundColor $ErrorColor
    Write-Host ""
    exit 1
}
finally {
    Pop-Location
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor $InfoColor
    Write-Host "Server stopped." -ForegroundColor $SuccessColor
    Write-Host "============================================================`n" -ForegroundColor $InfoColor
}
#endregion
