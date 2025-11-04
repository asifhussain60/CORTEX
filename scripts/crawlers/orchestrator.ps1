<#
.SYNOPSIS
    Multi-Threaded Crawler Orchestrator - Coordinates parallel area-specific crawlers

.DESCRIPTION
    Main coordinator for KDS v6.0 multi-threaded crawler system.
    Launches 5 area crawlers in parallel (UI, API, Service, Test, Database) as PowerShell jobs,
    displays real-time progress, and collects results for BRAIN feeding.
    
    Target: <5 min for 1000+ file projects (60% faster than single-threaded)

.PARAMETER WorkspaceRoot
    Absolute path to the project workspace root

.PARAMETER Mode
    Crawler mode: 'deep' (all crawlers) or 'quick' (UI and Test only)

.PARAMETER SkipBrainFeed
    If specified, crawlers run but BRAIN feeding is skipped (for testing)

.EXAMPLE
    .\orchestrator.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS"
    
.EXAMPLE
    .\orchestrator.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS" -Mode quick

.NOTES
    Version: 1.0.0
    Author: KDS Multi-Threaded Crawler System
    Performance Target: <5 min for 1000 files (60% improvement)
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceRoot,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet('deep', 'quick')]
    [string]$Mode = 'deep',
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBrainFeed
)

# Validate workspace root exists
if (-not (Test-Path $WorkspaceRoot)) {
    Write-Error "Workspace root not found: $WorkspaceRoot"
    exit 1
}

# Start overall timer
$totalStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔄 KDS Multi-Threaded Crawler Orchestrator" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceRoot" -ForegroundColor Gray
Write-Host "Mode: $Mode" -ForegroundColor Gray
Write-Host "Target: <5 min for 1000+ files (60% improvement)" -ForegroundColor Yellow
Write-Host ""

# Prepare output directory
# Normalize workspace root and detect KDS location
$normalizedRoot = $WorkspaceRoot.TrimEnd('\')
if ($normalizedRoot -match '\\KDS$') {
    # Workspace IS KDS
    $outputDir = "$normalizedRoot\kds-brain\crawler-temp"
} else {
    # KDS is inside workspace
    $outputDir = "$normalizedRoot\KDS\kds-brain\crawler-temp"
}

if (-not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

# Clean old results
Remove-Item "$outputDir\*.json" -Force -ErrorAction SilentlyContinue

# Define crawlers to run
$crawlers = @{}

# Determine script directory (handles both KDS as project and KDS as tool)
$scriptDir = Split-Path -Parent $PSCommandPath

if ($Mode -eq 'deep') {
    $crawlers = @{
        UI = "$scriptDir\ui-crawler.ps1"
        API = "$scriptDir\api-crawler.ps1"
        Service = "$scriptDir\service-crawler.ps1"
        Test = "$scriptDir\test-crawler.ps1"
        Database = "$scriptDir\database-crawler.ps1"
    }
} else {
    # Quick mode: UI and Test only (most valuable for TDD)
    $crawlers = @{
        UI = "$scriptDir\ui-crawler.ps1"
        Test = "$scriptDir\test-crawler.ps1"
    }
}

# Step 1: Launch parallel crawlers
Write-Host "[1/4] Launching parallel crawlers..." -ForegroundColor Yellow
Write-Host ""

$jobs = @{}
foreach ($area in $crawlers.Keys) {
    $scriptPath = $crawlers[$area]
    
    if (-not (Test-Path $scriptPath)) {
        Write-Warning "⚠️ Crawler script not found: $scriptPath"
        continue
    }
    
    Write-Host "  🚀 Starting $area crawler..." -ForegroundColor Gray
    
    $job = Start-Job -ScriptBlock {
        param($ScriptPath, $WorkspaceRoot)
        & $ScriptPath -WorkspaceRoot $WorkspaceRoot
    } -ArgumentList $scriptPath, $WorkspaceRoot
    
    $jobs[$area] = @{
        Job = $job
        StartTime = Get-Date
        Status = "Running"
        Duration = 0
    }
}

Write-Host ""
Write-Host "  ✅ $($jobs.Count) crawlers launched" -ForegroundColor Green
Write-Host ""

# Step 2: Monitor progress with real-time display
Write-Host "[2/4] Monitoring crawler progress..." -ForegroundColor Yellow
Write-Host ""

$refreshInterval = 2  # seconds

while ($jobs.Values.Job | Where-Object {$_.State -eq 'Running'}) {
    # Clear screen for clean display (optional - can be commented out)
    # Clear-Host
    
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "🔄 Multi-Threaded Crawler Progress" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "⏱️  Elapsed: $([int]$totalStopwatch.Elapsed.TotalMinutes)m $($totalStopwatch.Elapsed.Seconds)s | Target: <5 min" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($area in $jobs.Keys | Sort-Object) {
        $jobInfo = $jobs[$area]
        $job = $jobInfo.Job
        
        $duration = [int](New-TimeSpan -Start $jobInfo.StartTime -End (Get-Date)).TotalSeconds
        $jobInfo.Duration = $duration
        
        $statusIcon = switch ($job.State) {
            'Running' { "🔄" }
            'Completed' { "✅" }
            'Failed' { "❌" }
            default { "⚠️" }
        }
        
        $statusColor = switch ($job.State) {
            'Running' { "Yellow" }
            'Completed' { "Green" }
            'Failed' { "Red" }
            default { "Gray" }
        }
        
        $status = switch ($job.State) {
            'Running' { "In Progress" }
            'Completed' { "Complete ($($duration)s)" }
            'Failed' { "Failed" }
            default { $job.State }
        }
        
        $jobInfo.Status = $job.State
        
        Write-Host "$statusIcon $area Crawler: " -NoNewline
        Write-Host $status -ForegroundColor $statusColor
    }
    
    $completedCount = ($jobs.Values | Where-Object {$_.Status -eq 'Completed'}).Count
    $totalCount = $jobs.Count
    $progressPercent = [int](($completedCount / $totalCount) * 100)
    
    Write-Host ""
    Write-Host "Progress: $completedCount/$totalCount ($progressPercent%)" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    Start-Sleep -Seconds $refreshInterval
}

Write-Host ""

# Step 3: Collect results
Write-Host "[3/4] Collecting crawler results..." -ForegroundColor Yellow
Write-Host ""

$results = @{}
$failedCrawlers = @()

foreach ($area in $jobs.Keys) {
    $jobInfo = $jobs[$area]
    $job = $jobInfo.Job
    
    if ($job.State -eq 'Completed') {
        try {
            $output = Receive-Job -Job $job -ErrorAction Stop
            $results[$area] = $output
            Write-Host "  ✅ $area crawler: Success ($($jobInfo.Duration)s)" -ForegroundColor Green
        } catch {
            Write-Warning "  ⚠️ $area crawler: Failed to retrieve output - $_"
            $failedCrawlers += $area
        }
    } else {
        Write-Warning "  ❌ $area crawler: Failed with state $($job.State)"
        $failedCrawlers += $area
    }
    
    Remove-Job -Job $job -Force
}

Write-Host ""

# Step 4: Feed BRAIN (if not skipped)
if (-not $SkipBrainFeed) {
    Write-Host "[4/4] Feeding BRAIN with discoveries..." -ForegroundColor Yellow
    Write-Host ""
    
    $brainFeederPath = "$scriptDir\feed-brain.ps1"
    
    if (Test-Path $brainFeederPath) {
        try {
            & $brainFeederPath -WorkspaceRoot $WorkspaceRoot -Results $results
            Write-Host "  ✅ BRAIN updated successfully" -ForegroundColor Green
        } catch {
            Write-Warning "  ⚠️ BRAIN feeding failed: $_"
        }
    } else {
        Write-Warning "  ⚠️ BRAIN feeder not found: $brainFeederPath"
        Write-Host "  📁 Crawler results available in: $outputDir" -ForegroundColor Gray
    }
} else {
    Write-Host "[4/4] BRAIN feeding skipped (test mode)" -ForegroundColor Gray
    Write-Host "  📁 Crawler results available in: $outputDir" -ForegroundColor Gray
}

Write-Host ""

# Step 5: Summary report
$totalStopwatch.Stop()
$totalMinutes = [int]$totalStopwatch.Elapsed.TotalMinutes
$totalSeconds = $totalStopwatch.Elapsed.Seconds

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Multi-Threaded Crawler Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  Total time: ${totalMinutes}m ${totalSeconds}s" -ForegroundColor White
Write-Host "  Target: <5 min" -ForegroundColor $(if ($totalMinutes -lt 5) { "Green" } else { "Yellow" })
Write-Host "  Crawlers completed: $($results.Count)/$($jobs.Count)" -ForegroundColor White

if ($failedCrawlers.Count -gt 0) {
    Write-Host "  Failed crawlers: $($failedCrawlers -join ', ')" -ForegroundColor Red
}

Write-Host ""

# Display key statistics
if ($results.ContainsKey('UI')) {
    $uiStats = $results['UI'].statistics
    Write-Host "  🎨 UI: $($uiStats.total_components) components, $($uiStats.total_element_ids) element IDs" -ForegroundColor White
}

if ($results.ContainsKey('API')) {
    $apiStats = $results['API'].statistics
    Write-Host "  🌐 API: $($apiStats.total_controllers) controllers, $($apiStats.total_endpoints) endpoints" -ForegroundColor White
}

if ($results.ContainsKey('Service')) {
    $serviceStats = $results['Service'].statistics
    Write-Host "  ⚙️ Services: $($serviceStats.total_services) services, $($serviceStats.total_interfaces) interfaces" -ForegroundColor White
}

if ($results.ContainsKey('Test')) {
    $testStats = $results['Test'].statistics
    Write-Host "  🧪 Tests: $($testStats.total_tests) test files, $($testStats.total_selectors) selectors" -ForegroundColor White
}

if ($results.ContainsKey('Database')) {
    $dbStats = $results['Database'].statistics
    Write-Host "  🗄️  Database: $($dbStats.total_entities) entities, $($dbStats.total_connections) connections" -ForegroundColor White
}

Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan

# Performance comparison
if ($totalMinutes -lt 5) {
    $improvement = [int]((1 - ($totalStopwatch.Elapsed.TotalMinutes / 10)) * 100)
    Write-Host "🎯 Performance: $improvement% faster than baseline (10 min)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Performance: Did not meet <5 min target" -ForegroundColor Yellow
}

Write-Host ""

# Exit code
if ($failedCrawlers.Count -eq 0) {
    exit 0
} else {
    exit 1
}
