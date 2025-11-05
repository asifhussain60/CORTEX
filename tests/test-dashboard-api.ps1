#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Comprehensive test suite for KDS Dashboard API
.DESCRIPTION
    Validates that the dashboard API server is running correctly and all endpoints respond properly.
    This test should be run every time the dashboard is updated or launched.
.PARAMETER Port
    Port number where the API server is running (default: 8765)
.EXAMPLE
    .\test-dashboard-api.ps1
    .\test-dashboard-api.ps1 -Port 8765
#>

param(
    [int]$Port = 8765
)

$ErrorActionPreference = 'Continue'
$apiUrl = "http://localhost:$Port"

# Test results tracking
$script:testResults = @{
    Passed = 0
    Failed = 0
    Warnings = 0
    Details = @()
}

function Write-TestResult {
    param(
        [string]$TestName,
        [string]$Status,  # "PASS", "FAIL", "WARN"
        [string]$Message
    )
    
    $icon = switch ($Status) {
        "PASS" { "✅"; $script:testResults.Passed++ }
        "FAIL" { "❌"; $script:testResults.Failed++ }
        "WARN" { "⚠️"; $script:testResults.Warnings++ }
    }
    
    $color = switch ($Status) {
        "PASS" { "Green" }
        "FAIL" { "Red" }
        "WARN" { "Yellow" }
    }
    
    Write-Host "$icon [$Status] $TestName" -ForegroundColor $color
    if ($Message) {
        Write-Host "   $Message" -ForegroundColor Gray
    }
    
    $script:testResults.Details += @{
        Test = $TestName
        Status = $Status
        Message = $Message
    }
}

Write-Host ""
Write-Host "🧪 KDS Dashboard API Test Suite" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "API URL: $apiUrl" -ForegroundColor Gray
Write-Host ""

# Test 1: API Server is reachable
Write-Host "📋 Test Group 1: API Server Connectivity" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/api/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-TestResult "API Server Reachable" "PASS" "HTTP 200 OK"
    } else {
        Write-TestResult "API Server Reachable" "FAIL" "HTTP $($response.StatusCode)"
    }
} catch {
    Write-TestResult "API Server Reachable" "FAIL" $_.Exception.Message
    Write-Host ""
    Write-Host "❌ CRITICAL: API Server is not running or not responding" -ForegroundColor Red
    Write-Host "   Run: .\scripts\launch-dashboard.ps1 to start the server" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""

# Test 2: Health endpoint returns valid data
Write-Host "📋 Test Group 2: Health Endpoint" -ForegroundColor Cyan
Write-Host ""

try {
    $healthResponse = Invoke-RestMethod -Uri "$apiUrl/api/health" -Method Get -TimeoutSec 5
    
    # Check response structure
    if ($healthResponse.categories) {
        Write-TestResult "Health Data Structure" "PASS" "Categories array present"
    } else {
        Write-TestResult "Health Data Structure" "FAIL" "Missing 'categories' field"
    }
    
    # Check category count
    $categoryCount = $healthResponse.categories.Count
    if ($categoryCount -ge 5) {
        Write-TestResult "Health Categories Count" "PASS" "$categoryCount categories found"
    } else {
        Write-TestResult "Health Categories Count" "WARN" "Only $categoryCount categories (expected >= 5)"
    }
    
    # Check for required categories
    $requiredCategories = @('Infrastructure', 'Agents', 'BRAIN System', 'Sessions', 'Knowledge')
    foreach ($cat in $requiredCategories) {
        $found = $healthResponse.categories | Where-Object { $_.name -eq $cat }
        if ($found) {
            Write-TestResult "Category: $cat" "PASS" "Found with $($found.checks.Count) checks"
        } else {
            Write-TestResult "Category: $cat" "FAIL" "Missing category"
        }
    }
    
    # Check total checks
    $totalChecks = ($healthResponse.categories | ForEach-Object { $_.checks.Count } | Measure-Object -Sum).Sum
    if ($totalChecks -gt 0) {
        Write-TestResult "Total Health Checks" "PASS" "$totalChecks checks loaded"
    } else {
        Write-TestResult "Total Health Checks" "FAIL" "No checks found"
    }
    
} catch {
    Write-TestResult "Health Endpoint" "FAIL" $_.Exception.Message
}

Write-Host ""

# Test 3: Metrics endpoint returns valid data
Write-Host "📋 Test Group 3: Metrics Endpoint" -ForegroundColor Cyan
Write-Host ""

try {
    $metricsResponse = Invoke-RestMethod -Uri "$apiUrl/api/metrics" -Method Get -TimeoutSec 5
    
    # Check for required metric categories
    $requiredMetrics = @('brainHealth', 'routingAccuracy', 'knowledgeGraph', 'fileHotspots', 'eventActivity', 'testSuccess')
    foreach ($metric in $requiredMetrics) {
        if ($metricsResponse.PSObject.Properties.Name -contains $metric) {
            Write-TestResult "Metric: $metric" "PASS" "Present"
        } else {
            Write-TestResult "Metric: $metric" "FAIL" "Missing"
        }
    }
    
    # Validate brainHealth structure
    if ($metricsResponse.brainHealth) {
        $score = [int]$metricsResponse.brainHealth.score
        if ($score -ge 0 -and $score -le 100) {
            Write-TestResult "BRAIN Health Score" "PASS" "Score: $score%"
        } else {
            Write-TestResult "BRAIN Health Score" "FAIL" "Invalid score: $score"
        }
    }
    
    # Validate routingAccuracy structure
    if ($metricsResponse.routingAccuracy -and $metricsResponse.routingAccuracy.overall) {
        Write-TestResult "Routing Accuracy Data" "PASS" "Overall: $($metricsResponse.routingAccuracy.overall)%"
    } else {
        Write-TestResult "Routing Accuracy Data" "FAIL" "Invalid structure"
    }
    
} catch {
    Write-TestResult "Metrics Endpoint" "FAIL" $_.Exception.Message
}

Write-Host ""

# Test 4: BRAIN endpoint returns valid data
Write-Host "📋 Test Group 4: BRAIN Endpoint" -ForegroundColor Cyan
Write-Host ""

try {
    $brainResponse = Invoke-RestMethod -Uri "$apiUrl/api/health/brain" -Method Get -TimeoutSec 5
    
    if ($brainResponse.checks) {
        $brainChecks = $brainResponse.checks.Count
        Write-TestResult "BRAIN Checks Data" "PASS" "$brainChecks checks loaded"
        
        # Check for integrity checks
        $integrityChecks = $brainResponse.checks | Where-Object { $_.name -like "Integrity:*" }
        if ($integrityChecks.Count -ge 10) {
            Write-TestResult "BRAIN Integrity Checks" "PASS" "$($integrityChecks.Count) integrity checks"
        } else {
            Write-TestResult "BRAIN Integrity Checks" "WARN" "Only $($integrityChecks.Count) integrity checks"
        }
    } else {
        Write-TestResult "BRAIN Endpoint" "FAIL" "No checks data returned"
    }
    
} catch {
    Write-TestResult "BRAIN Endpoint" "FAIL" $_.Exception.Message
}

Write-Host ""

# Test 5: Response times
Write-Host "📋 Test Group 5: Performance" -ForegroundColor Cyan
Write-Host ""

# Measure health endpoint response time
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    Invoke-RestMethod -Uri "$apiUrl/api/health" -Method Get -TimeoutSec 5 | Out-Null
    $stopwatch.Stop()
    $healthTime = $stopwatch.ElapsedMilliseconds
    
    if ($healthTime -lt 2000) {
        Write-TestResult "Health Endpoint Response Time" "PASS" "${healthTime}ms (< 2000ms)"
    } elseif ($healthTime -lt 5000) {
        Write-TestResult "Health Endpoint Response Time" "WARN" "${healthTime}ms (slow but acceptable)"
    } else {
        Write-TestResult "Health Endpoint Response Time" "FAIL" "${healthTime}ms (> 5000ms - too slow)"
    }
} catch {
    Write-TestResult "Health Endpoint Response Time" "FAIL" $_.Exception.Message
}

# Measure metrics endpoint response time
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    Invoke-RestMethod -Uri "$apiUrl/api/metrics" -Method Get -TimeoutSec 5 | Out-Null
    $stopwatch.Stop()
    $metricsTime = $stopwatch.ElapsedMilliseconds
    
    if ($metricsTime -lt 2000) {
        Write-TestResult "Metrics Endpoint Response Time" "PASS" "${metricsTime}ms (< 2000ms)"
    } elseif ($metricsTime -lt 5000) {
        Write-TestResult "Metrics Endpoint Response Time" "WARN" "${metricsTime}ms (slow but acceptable)"
    } else {
        Write-TestResult "Metrics Endpoint Response Time" "FAIL" "${metricsTime}ms (> 5000ms - too slow)"
    }
} catch {
    Write-TestResult "Metrics Endpoint Response Time" "FAIL" $_.Exception.Message
}

Write-Host ""

# Test 6: CORS Headers (for browser compatibility)
Write-Host "📋 Test Group 6: CORS Configuration" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$apiUrl/api/health" -UseBasicParsing -TimeoutSec 5
    
    $corsHeader = $response.Headers['Access-Control-Allow-Origin']
    if ($corsHeader -eq '*') {
        Write-TestResult "CORS Headers" "PASS" "Access-Control-Allow-Origin: *"
    } else {
        Write-TestResult "CORS Headers" "WARN" "CORS may not be configured properly"
    }
} catch {
    Write-TestResult "CORS Headers" "FAIL" $_.Exception.Message
}

Write-Host ""

# Final Summary
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

$total = $script:testResults.Passed + $script:testResults.Failed + $script:testResults.Warnings
$passRate = if ($total -gt 0) { [math]::Round(($script:testResults.Passed / $total) * 100, 1) } else { 0 }

Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "✅ Passed:   $($script:testResults.Passed)" -ForegroundColor Green
Write-Host "❌ Failed:   $($script:testResults.Failed)" -ForegroundColor Red
Write-Host "⚠️  Warnings: $($script:testResults.Warnings)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 90) { "Green" } elseif ($passRate -ge 70) { "Yellow" } else { "Red" })
Write-Host ""

if ($script:testResults.Failed -eq 0) {
    Write-Host "✅ All critical tests passed!" -ForegroundColor Green
    Write-Host "   Dashboard is ready to use." -ForegroundColor Gray
    $exitCode = 0
} else {
    Write-Host "❌ $($script:testResults.Failed) test(s) failed!" -ForegroundColor Red
    Write-Host "   Dashboard may not function correctly." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Failed Tests:" -ForegroundColor Red
    $script:testResults.Details | Where-Object { $_.Status -eq "FAIL" } | ForEach-Object {
        Write-Host "  • $($_.Test): $($_.Message)" -ForegroundColor Gray
    }
    $exitCode = 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray

exit $exitCode
