# Validation Automation Script
# Purpose: Validate implementation against tests
# Triggers rollback if tests fail

param(
    [Parameter(Mandatory=$true)]
    [string]$TestFile,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

if (-not $DryRun -or $env:KDS_VERBOSE) {
    Write-Host "`n✔️  Running Validation" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

# In DryRun mode, simulate validation
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "  [DRY RUN] Would execute tests" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would detect failures" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would trigger rollback on failure" -ForegroundColor Yellow
    }
    
    return @{
        can_detect_failures = $true
        triggers_rollback = $true
        dry_run = $true
    }
}

# Real execution: Validate and potentially rollback
try {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n📝 Executing tests..." -ForegroundColor Cyan
    }
    
    # Execute tests
    $testResult = & "$workspaceRoot\scripts\left-brain\execute-tests.ps1" -TestFile $TestFile -Verbose:$Verbose
    
    $validationPassed = ($testResult.passed -eq $testResult.total) -and ($testResult.status -eq "success")
    
    if ($validationPassed) {
        if ($env:KDS_VERBOSE) {
            Write-Host "`n  ✅ Validation Passed: All tests green" -ForegroundColor Green
        }
        
        return @{
            validation_passed = $true
            rollback_needed = $false
            test_results = $testResult
        }
    } else {
        Write-Host "`n  ❌ Validation Failed: Tests failing" -ForegroundColor Red
        Write-Host "     Failed: $($testResult.failed)/$($testResult.total) tests" -ForegroundColor Red
        
        if ($env:KDS_VERBOSE) {
            Write-Host "`n  ⚠️  Triggering rollback..." -ForegroundColor Yellow
        }
        
        return @{
            validation_passed = $false
            rollback_needed = $true
            test_results = $testResult
        }
    }
    
} catch {
    Write-Host "`n  ❌ Validation error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        validation_passed = $false
        rollback_needed = $true
        error = $_.Exception.Message
    }
}
