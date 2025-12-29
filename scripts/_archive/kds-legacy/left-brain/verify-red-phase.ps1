# TDD RED Phase Verification Script
# Purpose: Verify tests fail initially (before implementation exists)
# This confirms we're following TDD: tests first, then implementation

param(
    [Parameter(Mandatory=$true)]
    [string]$TestFile,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

if (-not $DryRun -or $env:KDS_VERBOSE) {
    Write-Host "`n🔴 TDD RED Phase: Verifying Tests Fail" -ForegroundColor Red
    Write-Host "=" * 60 -ForegroundColor Red
    Write-Host "Test File: $TestFile" -ForegroundColor Gray
}

# In DryRun mode, simulate verification
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "  [DRY RUN] Would execute tests" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would verify tests fail" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would log to execution-state.jsonl" -ForegroundColor Yellow
    }
    
    return @{
        tests_failed = $true
        logged_failure = $true
        phase = "RED"
        dry_run = $true
    }
}

# Real execution: Run tests and verify they fail
try {
    # Execute tests
    $testResult = & "$workspaceRoot\scripts\left-brain\execute-tests.ps1" -TestFile $TestFile -Verbose:$Verbose
    
    # Verify tests failed (RED phase requirement)
    $testsFailed = ($testResult.failed -gt 0) -or ($testResult.status -eq "failed")
    
    if ($testsFailed) {
        if ($env:KDS_VERBOSE) {
            Write-Host "`n  ✅ RED Phase Confirmed: Tests fail as expected" -ForegroundColor Green
            Write-Host "     Failed: $($testResult.failed)/$($testResult.total) tests" -ForegroundColor Gray
        }
    } else {
        Write-Host "`n  ⚠️  WARNING: Tests passed in RED phase!" -ForegroundColor Yellow
        Write-Host "     This violates TDD - tests should fail before implementation exists" -ForegroundColor Yellow
    }
    
    # Log to execution state
    $timestamp = Get-Date -Format "o"
    $sessionId = if (Test-Path "$workspaceRoot\cortex-brain\right-hemisphere\active-plan.yaml") {
        $activePlan = Get-Content "$workspaceRoot\cortex-brain\right-hemisphere\active-plan.yaml" -Raw
        if ($activePlan -match 'session_id:\s*"([^"]+)"') { $Matches[1] } else { "unknown-session" }
    } else {
        "unknown-session"
    }
    
    $executionState = @{
        timestamp = $timestamp
        session_id = $sessionId
        task_id = "red-phase-verification"
        phase = "RED"
        status = if ($testsFailed) { "completed" } else { "warning" }
        tests_status = @{
            total = $testResult.total
            passed = $testResult.passed
            failed = $testResult.failed
        }
        test_file = $TestFile
    }
    
    $executionStateFile = Join-Path $workspaceRoot "cortex-brain\left-hemisphere\execution-state.jsonl"
    $executionStateJson = $executionState | ConvertTo-Json -Compress
    Add-Content -Path $executionStateFile -Value $executionStateJson
    
    if ($env:KDS_VERBOSE) {
        Write-Host "  ✅ Logged verification to execution-state.jsonl" -ForegroundColor Green
    }
    
    return @{
        tests_failed = $testsFailed
        logged_failure = $true
        phase = "RED"
        test_results = $testResult
    }
    
} catch {
    throw "RED phase verification failed: $($_.Exception.Message)"
}
