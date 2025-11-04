# TDD GREEN Phase Verification Script
# Purpose: Verify tests pass after implementation
# This confirms GREEN phase: implementation makes tests pass

param(
    [Parameter(Mandatory=$true)]
    [string]$TestFile
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

if ($env:KDS_VERBOSE) {
    Write-Host "`n🟢 TDD GREEN Phase: Verifying Tests Pass" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
}

try {
    # Execute tests
    $testResult = & "$workspaceRoot\scripts\left-brain\execute-tests.ps1" -TestFile $TestFile
    
    # Verify tests passed (GREEN phase requirement)
    $testsPassed = ($testResult.passed -eq $testResult.total) -and ($testResult.status -eq "success")
    
    if ($testsPassed) {
        if ($env:KDS_VERBOSE) {
            Write-Host "`n  ✅ GREEN Phase Confirmed: All tests pass" -ForegroundColor Green
            Write-Host "     Passed: $($testResult.passed)/$($testResult.total) tests" -ForegroundColor Gray
        }
    } else {
        Write-Host "`n  ❌ GREEN Phase Failed: Tests still failing" -ForegroundColor Red
        Write-Host "     Failed: $($testResult.failed)/$($testResult.total) tests" -ForegroundColor Red
    }
    
    # Log to execution state
    $timestamp = Get-Date -Format "o"
    $sessionId = if (Test-Path "$workspaceRoot\kds-brain\right-hemisphere\active-plan.yaml") {
        $activePlan = Get-Content "$workspaceRoot\kds-brain\right-hemisphere\active-plan.yaml" -Raw
        if ($activePlan -match 'session_id:\s*"([^"]+)"') { $Matches[1] } else { "unknown-session" }
    } else {
        "unknown-session"
    }
    
    $executionState = @{
        timestamp = $timestamp
        session_id = $sessionId
        task_id = "green-phase-verification"
        phase = "GREEN"
        status = if ($testsPassed) { "completed" } else { "failed" }
        tests_status = @{
            total = $testResult.total
            passed = $testResult.passed
            failed = $testResult.failed
        }
        test_file = $TestFile
    }
    
    $executionStateFile = Join-Path $workspaceRoot "kds-brain\left-hemisphere\execution-state.jsonl"
    $executionStateJson = $executionState | ConvertTo-Json -Compress
    Add-Content -Path $executionStateFile -Value $executionStateJson
    
    return @{
        tests_passed = $testsPassed
        phase = "GREEN"
        test_results = $testResult
    }
    
} catch {
    throw "GREEN phase verification failed: $($_.Exception.Message)"
}
