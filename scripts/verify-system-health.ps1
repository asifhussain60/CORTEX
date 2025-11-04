# KDS System Health Verification Script
# Purpose: Run all test suites and provide comprehensive health assessment
# Usage: .\KDS\scripts\verify-system-health.ps1 [-Verbose] [-QuickCheck]

param(
    [switch]$Verbose,
    [switch]$QuickCheck  # Run only essential tests (faster)
)

$ErrorActionPreference = "Stop"

Write-Host "`n🔍 KDS System Health Verification" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "Version: 1.0" -ForegroundColor Gray
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host ""

# Initialize results tracking
$results = @{
    total_suites = 0
    passed_suites = 0
    failed_suites = 0
    skipped_suites = 0
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warnings = 0
    start_time = Get-Date
    suite_details = @()
}

# Helper function to run test suite
function Invoke-TestSuite {
    param(
        [string]$Name,
        [string]$ScriptPath,
        [switch]$Essential,  # Must run even in QuickCheck mode
        [switch]$JsonOutput
    )
    
    if ($QuickCheck -and -not $Essential) {
        Write-Host "📊 Suite: $Name" -ForegroundColor Yellow
        Write-Host "  ⏭️  SKIPPED (QuickCheck mode)" -ForegroundColor Gray
        $results.total_suites++
        $results.skipped_suites++
        
        $results.suite_details += @{
            name = $Name
            status = "SKIPPED"
            reason = "QuickCheck mode"
        }
        
        return
    }
    
    Write-Host "📊 Suite: $Name" -ForegroundColor Yellow
    Write-Host "  ⏳ Running: $ScriptPath" -ForegroundColor Gray
    
    $results.total_suites++
    
    try {
        if ($JsonOutput) {
            # Parse JSON output for detailed stats
            $output = & $ScriptPath -JsonOutput 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                $json = $output | ConvertFrom-Json -ErrorAction Stop
                
                $results.passed_suites++
                $results.total_tests += $json.total_checks
                $results.passed_tests += $json.passed
                $results.failed_tests += $json.failed
                $results.warnings += $json.warnings
                
                Write-Host "  ✅ PASSED ($($json.passed)/$($json.total_checks) checks)" -ForegroundColor Green
                
                $results.suite_details += @{
                    name = $Name
                    status = "PASSED"
                    total_checks = $json.total_checks
                    passed = $json.passed
                    failed = $json.failed
                    warnings = $json.warnings
                    execution_time_ms = $json.execution_time_ms
                }
            } else {
                $results.failed_suites++
                Write-Host "  ❌ FAILED" -ForegroundColor Red
                
                $results.suite_details += @{
                    name = $Name
                    status = "FAILED"
                    error = "Non-zero exit code: $LASTEXITCODE"
                }
            }
        } else {
            # Run test and check exit code only
            if ($Verbose) {
                & $ScriptPath
            } else {
                & $ScriptPath | Out-Null
            }
            
            $exitCode = $LASTEXITCODE
            
            if ($exitCode -eq 0) {
                $results.passed_suites++
                Write-Host "  ✅ PASSED" -ForegroundColor Green
                
                $results.suite_details += @{
                    name = $Name
                    status = "PASSED"
                }
            } else {
                $results.failed_suites++
                Write-Host "  ❌ FAILED (exit code: $exitCode)" -ForegroundColor Red
                
                $results.suite_details += @{
                    name = $Name
                    status = "FAILED"
                    exit_code = $exitCode
                }
            }
        }
    } catch {
        $results.failed_suites++
        Write-Host "  ❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
        
        $results.suite_details += @{
            name = $Name
            status = "ERROR"
            error = $_.Exception.Message
        }
    }
    
    Write-Host ""
}

# Validate workspace
$kdsRoot = Split-Path $PSScriptRoot -Parent
if (-not (Test-Path "$kdsRoot\kds-brain")) {
    Write-Host "❌ ERROR: KDS BRAIN directory not found" -ForegroundColor Red
    Write-Host "   Expected: $kdsRoot\kds-brain" -ForegroundColor Gray
    exit 1
}

Write-Host "Workspace: $kdsRoot" -ForegroundColor Gray
Write-Host "Mode: $(if ($QuickCheck) { 'Quick Check (Essential Tests Only)' } else { 'Full Verification' })" -ForegroundColor Gray
Write-Host ""

# ============================================================================
# Essential Tests (Always Run)
# ============================================================================
Write-Host "🔬 ESSENTIAL TESTS (Always Run)" -ForegroundColor Magenta
Write-Host ""

# Test 1: Brain Integrity (ESSENTIAL)
Invoke-TestSuite `
    -Name "Brain Integrity" `
    -ScriptPath "$kdsRoot\tests\test-brain-integrity.ps1" `
    -Essential `
    -JsonOutput

# Test 2: Week 4 Validation (ESSENTIAL)
Invoke-TestSuite `
    -Name "Week 4 Progressive Validation" `
    -ScriptPath "$kdsRoot\tests\v6-progressive\week4-validation.ps1" `
    -Essential

# Test 3: E2E Acceptance (ESSENTIAL)
Invoke-TestSuite `
    -Name "E2E Brain Acceptance" `
    -ScriptPath "$kdsRoot\tests\e2e\brain-acceptance-test.ps1" `
    -Essential

# ============================================================================
# Extended Tests (Full Verification Only)
# ============================================================================
if (-not $QuickCheck) {
    Write-Host "🔬 EXTENDED TESTS (Full Verification)" -ForegroundColor Magenta
    Write-Host ""
    
    # Test 4: Week 1 Validation
    Invoke-TestSuite `
        -Name "Week 1 Progressive Validation (Infrastructure)" `
        -ScriptPath "$kdsRoot\tests\v6-progressive\week1-validation.ps1"
    
    # Test 5: Week 2 Validation
    Invoke-TestSuite `
        -Name "Week 2 Progressive Validation (Routing & Events)" `
        -ScriptPath "$kdsRoot\tests\v6-progressive\week2-validation.ps1"
    
    # Test 6: Week 3 Validation
    Invoke-TestSuite `
        -Name "Week 3 Progressive Validation (BRAIN Intelligence)" `
        -ScriptPath "$kdsRoot\tests\v6-progressive\week3-validation.ps1"
    
    # Test 7: Dashboard Loading States
    Invoke-TestSuite `
        -Name "Dashboard Loading States" `
        -ScriptPath "$kdsRoot\tests\test-dashboard-loading-states.ps1"
    
    # Test 8: Dashboard Refresh
    Invoke-TestSuite `
        -Name "Dashboard Refresh Functionality" `
        -ScriptPath "$kdsRoot\tests\test-dashboard-refresh.ps1"
}

# ============================================================================
# Calculate Statistics
# ============================================================================
$results.end_time = Get-Date
$duration = $results.end_time - $results.start_time

$passRate = if ($results.total_suites -gt 0) {
    [math]::Round(($results.passed_suites / $results.total_suites) * 100, 1)
} else {
    0
}

# ============================================================================
# Display Summary
# ============================================================================
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "📊 VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

Write-Host "Execution Time:  $($duration.ToString('mm\:ss'))" -ForegroundColor White
Write-Host ""

Write-Host "Test Suites:" -ForegroundColor White
Write-Host "  Total:    $($results.total_suites)" -ForegroundColor Gray
Write-Host "  ✅ Passed: $($results.passed_suites)" -ForegroundColor Green
Write-Host "  ❌ Failed: $($results.failed_suites)" -ForegroundColor $(if ($results.failed_suites -eq 0) { "Gray" } else { "Red" })
Write-Host "  ⏭️  Skipped: $($results.skipped_suites)" -ForegroundColor Gray
Write-Host "  Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -eq 100) { "Green" } elseif ($passRate -ge 90) { "Yellow" } else { "Red" })
Write-Host ""

if ($results.total_tests -gt 0) {
    Write-Host "Individual Tests:" -ForegroundColor White
    Write-Host "  Total:    $($results.total_tests)" -ForegroundColor Gray
    Write-Host "  ✅ Passed: $($results.passed_tests)" -ForegroundColor Green
    Write-Host "  ❌ Failed: $($results.failed_tests)" -ForegroundColor $(if ($results.failed_tests -eq 0) { "Gray" } else { "Red" })
    Write-Host "  ⚠️  Warnings: $($results.warnings)" -ForegroundColor $(if ($results.warnings -eq 0) { "Gray" } else { "Yellow" })
    Write-Host ""
}

# ============================================================================
# Health Assessment
# ============================================================================
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "🏥 HEALTH ASSESSMENT" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

if ($results.failed_suites -eq 0) {
    Write-Host "✅ KDS SYSTEM IS HEALTHY AND OPTIMIZED!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your KDS system is configured for:" -ForegroundColor White
    Write-Host "  ✅ Maximum efficiency (routing, planning, execution)" -ForegroundColor Green
    Write-Host "  ✅ Maximum accuracy (BRAIN learning, pattern matching)" -ForegroundColor Green
    Write-Host "  ✅ Production readiness (all validations passing)" -ForegroundColor Green
    Write-Host ""
    
    # Additional insights
    if ($results.warnings -gt 0) {
        Write-Host "⚠️  Note: $($results.warnings) warning(s) detected" -ForegroundColor Yellow
        Write-Host "   Review detailed output for optimization opportunities" -ForegroundColor Gray
        Write-Host ""
    }
    
} elseif ($passRate -ge 80) {
    Write-Host "⚠️  KDS SYSTEM IS FUNCTIONAL WITH MINOR ISSUES" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "System Status:" -ForegroundColor White
    Write-Host "  ✅ Core functionality working" -ForegroundColor Green
    Write-Host "  ⚠️  $($results.failed_suites) suite(s) failing" -ForegroundColor Yellow
    Write-Host "  📋 Review failures for optimization" -ForegroundColor Gray
    Write-Host ""
    
} else {
    Write-Host "❌ KDS SYSTEM HAS SIGNIFICANT ISSUES" -ForegroundColor Red
    Write-Host ""
    Write-Host "System Status:" -ForegroundColor White
    Write-Host "  ❌ $($results.failed_suites) suite(s) failing" -ForegroundColor Red
    Write-Host "  ⚠️  System may not be fully functional" -ForegroundColor Yellow
    Write-Host "  🔧 Immediate action required" -ForegroundColor Red
    Write-Host ""
}

# ============================================================================
# Failed Tests Details
# ============================================================================
if ($results.failed_suites -gt 0) {
    Write-Host ("=" * 70) -ForegroundColor Red
    Write-Host "❌ FAILED TESTS" -ForegroundColor Red
    Write-Host ("=" * 70) -ForegroundColor Red
    Write-Host ""
    
    $failedSuites = $results.suite_details | Where-Object { $_.status -in @("FAILED", "ERROR") }
    
    foreach ($suite in $failedSuites) {
        Write-Host "❌ $($suite.name)" -ForegroundColor Red
        
        if ($suite.error) {
            Write-Host "   Error: $($suite.error)" -ForegroundColor Gray
        }
        
        if ($suite.exit_code) {
            Write-Host "   Exit Code: $($suite.exit_code)" -ForegroundColor Gray
        }
        
        if ($suite.failed -gt 0) {
            Write-Host "   Failed Checks: $($suite.failed)" -ForegroundColor Gray
        }
        
        Write-Host ""
    }
    
    Write-Host "📋 Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Run failed test with -Verbose for details" -ForegroundColor White
    Write-Host "  2. Check KDS/kds-brain/ for file corruption" -ForegroundColor White
    Write-Host "  3. Review events.jsonl for errors" -ForegroundColor White
    Write-Host "  4. Validate knowledge-graph.yaml syntax" -ForegroundColor White
    Write-Host ""
}

# ============================================================================
# Recommendations
# ============================================================================
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "💡 RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

if ($QuickCheck) {
    Write-Host "You ran a Quick Check (essential tests only)." -ForegroundColor White
    Write-Host ""
    Write-Host "For comprehensive verification, run:" -ForegroundColor Gray
    Write-Host "  .\KDS\scripts\verify-system-health.ps1" -ForegroundColor Yellow
    Write-Host ""
}

if ($results.failed_suites -eq 0) {
    Write-Host "✅ Continue current development workflow" -ForegroundColor Green
    Write-Host "✅ Run this verification weekly to track health" -ForegroundColor Green
    Write-Host "✅ Monitor BRAIN learning (should accumulate patterns)" -ForegroundColor Green
} else {
    Write-Host "🔧 Address failed tests before continuing development" -ForegroundColor Yellow
    Write-Host "📖 Review: KDS/docs/TEST-BASED-SYSTEM-VERIFICATION.md" -ForegroundColor Yellow
    Write-Host "🧠 Check BRAIN integrity: .\KDS\tests\test-brain-integrity.ps1 -Verbose" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# Exit Code
# ============================================================================
$exitCode = if ($results.failed_suites -eq 0) { 0 } else { 1 }

if ($Verbose) {
    Write-Host "Exit Code: $exitCode" -ForegroundColor Gray
}

exit $exitCode
