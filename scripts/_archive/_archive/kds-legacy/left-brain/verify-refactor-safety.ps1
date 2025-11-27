# Verify Refactor Safety Script
# Purpose: Ensure tests still pass after refactoring
# Critical: Tests must remain green during REFACTOR phase

param(
    [Parameter(Mandatory=$true)]
    [string]$TestFile
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

if ($env:KDS_VERBOSE) {
    Write-Host "`n🔵 Verifying Refactor Safety" -ForegroundColor Blue
    Write-Host "=" * 60 -ForegroundColor Blue
}

try {
    # Execute tests to verify they still pass
    $testResult = & "$workspaceRoot\scripts\left-brain\execute-tests.ps1" -TestFile $TestFile
    
    $testsStillPass = ($testResult.passed -eq $testResult.total) -and ($testResult.status -eq "success")
    
    if ($testsStillPass) {
        if ($env:KDS_VERBOSE) {
            Write-Host "`n  ✅ REFACTOR Safe: Tests still passing" -ForegroundColor Green
            Write-Host "     Passed: $($testResult.passed)/$($testResult.total) tests" -ForegroundColor Gray
        }
    } else {
        Write-Host "`n  ❌ REFACTOR Broke Tests!" -ForegroundColor Red
        Write-Host "     Failed: $($testResult.failed)/$($testResult.total) tests" -ForegroundColor Red
        Write-Host "     Rollback recommended" -ForegroundColor Yellow
    }
    
    return @{
        tests_still_pass = $testsStillPass
        test_results = $testResult
        safe_to_commit = $testsStillPass
    }
    
} catch {
    throw "Refactor safety verification failed: $($_.Exception.Message)"
}
