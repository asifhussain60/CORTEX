# TDD Auto Test Runner Script
# Purpose: Automatically re-run tests after code changes
# Used in GREEN and REFACTOR phases to validate changes

param(
    [Parameter(Mandatory=$true)]
    [string]$TestFile,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

if ($env:KDS_VERBOSE) {
    Write-Host "`n🔄 Auto Test Runner: Validating Changes" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

# In DryRun mode, simulate test execution
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "  [DRY RUN] Would execute tests" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would validate GREEN phase" -ForegroundColor Yellow
    }
    
    return @{
        tests_executed = $true
        validates_green_phase = $true
        dry_run = $true
    }
}

# Real execution: Run tests and validate
try {
    $testResult = & "$workspaceRoot\scripts\left-brain\execute-tests.ps1" -TestFile $TestFile -Verbose:$Verbose
    
    $allTestsPass = ($testResult.passed -eq $testResult.total) -and ($testResult.status -eq "success")
    
    if ($allTestsPass) {
        if ($env:KDS_VERBOSE) {
            Write-Host "`n  ✅ All tests passing ($($testResult.passed)/$($testResult.total))" -ForegroundColor Green
        }
    } else {
        Write-Host "`n  ❌ Tests failing ($($testResult.failed)/$($testResult.total) failed)" -ForegroundColor Red
    }
    
    return @{
        tests_executed = $true
        validates_green_phase = $allTestsPass
        test_results = $testResult
    }
    
} catch {
    throw "Auto test runner failed: $($_.Exception.Message)"
}
