<#
.SYNOPSIS
    Test Crawler - Discovers test patterns, frameworks, and selectors

.DESCRIPTION
    Area-specific crawler for tests. Discovers:
    - Test frameworks (Playwright, xUnit, Jest, pytest)
    - Test patterns (unit, integration, E2E, visual)
    - Selector strategies (data-testid, #element-id, text-based)
    - Test data (session tokens, mock data)
    - Coverage gaps
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.NOTES
    Version: 1.0.0
    Performance Target: <1.5 min for 200 tests
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceRoot,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "$WorkspaceRoot\KDS\kds-brain\crawler-temp\test-results.json"
)

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$startTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

Write-Host "🧪 Test Crawler Started" -ForegroundColor Cyan

$testPatterns = @("*.spec.ts", "*.spec.js", "*Test.cs", "*Tests.cs", "*.test.ts", "*.test.js")
$excludeDirs = @("node_modules", "bin", "obj", "dist")

$result = @{
    area = "Tests"
    scan_time = $startTime
    duration_seconds = 0
    workspace_root = $WorkspaceRoot
    tests = @()
    patterns = @{
        framework = "unknown"
        selector_strategy = "unknown"
        test_types = @()
    }
    coverage = @{
        files_with_tests = 0
        files_without_tests = 0
        coverage_percentage = 0
    }
    statistics = @{
        total_tests = 0
        total_selectors = 0
    }
}

# Helper: Detect test framework
function Get-TestFramework {
    param([string]$Content)
    
    if ($Content -match '@playwright/test|playwright') { return "Playwright" }
    if ($Content -match 'jest|@testing-library') { return "Jest" }
    if ($Content -match '\[Fact\]|\[Theory\]|xunit') { return "xUnit" }
    if ($Content -match '@Test|junit') { return "JUnit" }
    if ($Content -match 'pytest|unittest') { return "pytest" }
    return "unknown"
}

# Helper: Extract selectors
function Get-Selectors {
    param([string]$Content)
    
    $selectors = @()
    
    # Playwright locators: page.locator('#id') or page.locator('[data-testid="..."]')
    $matches = [regex]::Matches($Content, "\.locator\([`'\""]([^`'\""]+ )[`'\"\"]\)")
    foreach ($match in $matches) {
        $selector = $match.Groups[1].Value
        $type = if ($selector -match '^#') { "id" }
                elseif ($selector -match 'data-testid') { "data-testid" }
                elseif ($selector -match 'has-text|text=') { "text-based" }
                else { "css" }
        
        $selectors += @{
            type = $type
            value = $selector
        }
    }
    
    return $selectors
}

# Helper: Extract test data
function Get-TestData {
    param([string]$Content)
    
    $data = @{}
    
    # Session tokens (e.g., PQ9N5YWW)
    $match = [regex]::Match($Content, '(token|sessionToken)\s*[=:]\s*[`'\""]([A-Z0-9]{8})[`'\""]')
    if ($match.Success) {
        $data["session_token"] = $match.Groups[2].Value
    }
    
    # URLs (e.g., localhost:9091/host/control-panel)
    $match = [regex]::Match($Content, '(url|hostUrl)\s*[=:]\s*[`'\""]([^`'\""]*/host/[^`'\"\"]*)[`'\""]')
    if ($match.Success) {
        $data["host_url"] = $match.Groups[2].Value
    }
    
    return $data
}

# Helper: Classify test type
function Get-TestType {
    param([string]$Content, [string]$FileName)
    
    $types = @()
    
    if ($Content -match 'percySnapshot|visual') { $types += "visual" }
    if ($Content -match '\.spec\.|E2E|e2e') { $types += "e2e" }
    if ($Content -match 'integration|Integration') { $types += "integration" }
    if ($Content -match 'unit|Unit|\[Fact\]') { $types += "unit" }
    
    return $types
}

# Step 1: Discover tests
Write-Host "`n[1/3] Discovering test files..." -ForegroundColor Yellow

$testFiles = @()
foreach ($pattern in $testPatterns) {
    $files = Get-ChildItem -Path $WorkspaceRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    $testFiles += $files
}

Write-Host "  Found $($testFiles.Count) test files" -ForegroundColor Green

# Step 2: Parse tests
Write-Host "`n[2/3] Parsing test patterns..." -ForegroundColor Yellow

$frameworkCounts = @{}
$selectorTypes = @{}
$allTestTypes = @{}

foreach ($file in $testFiles) {
    Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        $framework = Get-TestFramework -Content $content
        $selectors = Get-Selectors -Content $content
        $testData = Get-TestData -Content $content
        $testTypes = Get-TestType -Content $content -FileName $file.Name
        
        $frameworkCounts[$framework] = ($frameworkCounts[$framework] ?? 0) + 1
        foreach ($sel in $selectors) {
            $selectorTypes[$sel.type] = ($selectorTypes[$sel.type] ?? 0) + 1
        }
        foreach ($type in $testTypes) {
            $allTestTypes[$type] = ($allTestTypes[$type] ?? 0) + 1
        }
        
        $test = @{
            path = $relativePath
            framework = $framework
            type = $testTypes -join ", "
            selectors = $selectors
            test_data = $testData
        }
        
        $result.tests += $test
        $result.statistics.total_tests++
        $result.statistics.total_selectors += $selectors.Count
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

# Step 3: Detect patterns and calculate coverage
Write-Host "`n[3/3] Detecting patterns..." -ForegroundColor Yellow

$result.patterns.framework = ($frameworkCounts.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key ?? "unknown"
$result.patterns.selector_strategy = ($selectorTypes.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key ?? "unknown"
$result.patterns.test_types = @($allTestTypes.Keys)

# Simple coverage heuristic: Files with tests vs total code files
$result.coverage.files_with_tests = $result.tests.Count
$result.coverage.files_without_tests = 0  # Would need full file scan to calculate accurately
$result.coverage.coverage_percentage = 0  # Placeholder

$stopwatch.Stop()
$result.duration_seconds = [int]$stopwatch.Elapsed.TotalSeconds

$outputDir = Split-Path -Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "`n✅ Test Crawler Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Test files: $($result.statistics.total_tests)" -ForegroundColor White
Write-Host "Selectors: $($result.statistics.total_selectors)" -ForegroundColor White
Write-Host "Framework: $($result.patterns.framework)" -ForegroundColor White
Write-Host "Duration: $($result.duration_seconds)s" -ForegroundColor White
Write-Host "════════════════════════════════════" -ForegroundColor Cyan

return $result
