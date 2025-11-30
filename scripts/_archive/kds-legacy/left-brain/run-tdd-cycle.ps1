# TDD Cycle Orchestrator
# Purpose: Execute complete RED→GREEN→REFACTOR TDD cycle
# This is the master script that coordinates all TDD phases

param(
    [Parameter(Mandatory=$true)]
    [string]$FeatureConfig,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

Write-Host "`n🔄 TDD Cycle Orchestrator" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Feature Config: $FeatureConfig" -ForegroundColor Gray
Write-Host ""

# Load feature configuration
if (-not (Test-Path $FeatureConfig)) {
    throw "Feature config not found: $FeatureConfig"
}

$configContent = Get-Content $FeatureConfig -Raw
$featureName = if ($configContent -match 'feature_name:\s*"([^"]+)"') { $Matches[1] } else { "Unknown Feature" }

Write-Host "🎯 Feature: $featureName" -ForegroundColor Cyan
Write-Host ""

# Extract test file path
$testFilePath = $null
if ($configContent -match 'tests:\s*-\s*path:\s*"([^"]+)"') {
    $testFilePath = Join-Path $workspaceRoot $Matches[1]
}

# Extract implementation file path
$implFilePath = $null
if ($configContent -match 'implementation:\s*-\s*path:\s*"([^"]+)"') {
    $implFilePath = Join-Path $workspaceRoot $Matches[1]
}

# Initialize orchestration state
$orchestrationState = @{
    feature_name = $featureName
    executed_red = $false
    executed_green = $false
    executed_refactor = $false
    all_phases_logged = $false
    status = "INIT"
    start_time = Get-Date
}

# DryRun mode simulation
if ($DryRun) {
    Write-Host "⚠️  DRY RUN MODE - Simulating TDD cycle" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "🔴 Phase 1: RED (Create failing tests)" -ForegroundColor Red
    Write-Host "  [DRY RUN] Would create tests" -ForegroundColor Yellow
    Write-Host "  [DRY RUN] Would verify tests fail" -ForegroundColor Yellow
    $orchestrationState.executed_red = $true
    
    Write-Host "`n🟢 Phase 2: GREEN (Make tests pass)" -ForegroundColor Green
    Write-Host "  [DRY RUN] Would implement code" -ForegroundColor Yellow
    Write-Host "  [DRY RUN] Would verify tests pass" -ForegroundColor Yellow
    $orchestrationState.executed_green = $true
    
    Write-Host "`n🔵 Phase 3: REFACTOR (Optimize code)" -ForegroundColor Blue
    Write-Host "  [DRY RUN] Would refactor code" -ForegroundColor Yellow
    Write-Host "  [DRY RUN] Would verify tests still pass" -ForegroundColor Yellow
    $orchestrationState.executed_refactor = $true
    
    Write-Host "`n📝 Logging" -ForegroundColor Cyan
    Write-Host "  [DRY RUN] Would log all phases to execution-state.jsonl" -ForegroundColor Yellow
    $orchestrationState.all_phases_logged = $true
    
    $orchestrationState.status = "COMPLETE"
    
    Write-Host "`n✅ TDD Cycle Complete (DRY RUN)" -ForegroundColor Green
    
    return $orchestrationState
}

# Real execution: Run full TDD cycle
try {
    # ========================================================================
    # PHASE 1: RED - Create tests that fail
    # ========================================================================
    Write-Host "🔴 Phase 1: RED (Create failing tests)" -ForegroundColor Red
    Write-Host "-" * 80 -ForegroundColor Red
    
    # Create tests
    $redCreate = & "$workspaceRoot\scripts\left-brain\create-tests.ps1" `
        -FeatureConfig $FeatureConfig `
        -Verbose:$Verbose
    
    if ($redCreate.tests_created) {
        Write-Host "  ✅ Tests created" -ForegroundColor Green
    } else {
        throw "RED phase failed: Could not create tests"
    }
    
    # Verify tests fail (if test file was created)
    if ($testFilePath -and (Test-Path $testFilePath)) {
        $redVerify = & "$workspaceRoot\scripts\left-brain\verify-red-phase.ps1" `
            -TestFile $testFilePath `
            -Verbose:$Verbose
        
        if ($redVerify.tests_failed) {
            Write-Host "  ✅ Tests fail as expected (RED phase confirmed)" -ForegroundColor Green
        } else {
            Write-Host "  ⚠️  Tests passed in RED phase (unexpected)" -ForegroundColor Yellow
        }
    }
    
    $orchestrationState.executed_red = $true
    Write-Host ""
    
    # ========================================================================
    # PHASE 2: GREEN - Implement code to make tests pass
    # ========================================================================
    Write-Host "🟢 Phase 2: GREEN (Make tests pass)" -ForegroundColor Green
    Write-Host "-" * 80 -ForegroundColor Green
    
    # Implement code
    $greenImpl = & "$workspaceRoot\scripts\left-brain\implement-code.ps1" `
        -FeatureConfig $FeatureConfig `
        -Verbose:$Verbose
    
    if ($greenImpl.code_created) {
        Write-Host "  ✅ Implementation created" -ForegroundColor Green
    } else {
        throw "GREEN phase failed: Could not create implementation"
    }
    
    # Verify tests pass (if test file exists)
    if ($testFilePath -and (Test-Path $testFilePath)) {
        $greenVerify = & "$workspaceRoot\scripts\left-brain\verify-green-phase.ps1" `
            -TestFile $testFilePath `
            -Verbose:$Verbose
        
        if ($greenVerify.tests_passed) {
            Write-Host "  ✅ All tests passing (GREEN phase confirmed)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Tests still failing - triggering rollback" -ForegroundColor Red
            
            & "$workspaceRoot\scripts\left-brain\rollback-changes.ps1" -Verbose:$Verbose
            throw "GREEN phase failed: Tests did not pass after implementation"
        }
    }
    
    $orchestrationState.executed_green = $true
    Write-Host ""
    
    # ========================================================================
    # PHASE 3: REFACTOR - Optimize code while keeping tests green
    # ========================================================================
    Write-Host "🔵 Phase 3: REFACTOR (Optimize code)" -ForegroundColor Blue
    Write-Host "-" * 80 -ForegroundColor Blue
    
    # Refactor code (if implementation file exists)
    if ($implFilePath -and (Test-Path $implFilePath)) {
        $refactor = & "$workspaceRoot\scripts\left-brain\refactor-code.ps1" `
            -File $implFilePath `
            -Verbose:$Verbose
        
        if ($refactor.code_optimized) {
            Write-Host "  ✅ Code refactored" -ForegroundColor Green
        }
        
        # Verify tests still pass after refactoring
        if ($testFilePath -and (Test-Path $testFilePath)) {
            $refactorVerify = & "$workspaceRoot\scripts\left-brain\verify-refactor-safety.ps1" `
                -TestFile $testFilePath `
                -Verbose:$Verbose
            
            if ($refactorVerify.tests_still_pass) {
                Write-Host "  ✅ Tests still passing after refactor" -ForegroundColor Green
            } else {
                Write-Host "  ❌ Refactor broke tests - triggering rollback" -ForegroundColor Red
                
                & "$workspaceRoot\scripts\left-brain\rollback-changes.ps1" -Verbose:$Verbose
                throw "REFACTOR phase failed: Tests failed after refactoring"
            }
        }
    }
    
    $orchestrationState.executed_refactor = $true
    $orchestrationState.all_phases_logged = $true  # Each phase logs individually
    Write-Host ""
    
    # ========================================================================
    # COMPLETION
    # ========================================================================
    $orchestrationState.status = "COMPLETE"
    $orchestrationState.end_time = Get-Date
    $orchestrationState.duration_seconds = ($orchestrationState.end_time - $orchestrationState.start_time).TotalSeconds
    
    # Send coordination message to RIGHT hemisphere
    $coordinationMessage = @{
        from = "left"
        to = "right"
        message_type = "TDD_CYCLE_COMPLETE"
        timestamp = (Get-Date -Format "o")
        data = @{
            feature_name = $featureName
            all_tests_passing = $true
            duration_seconds = $orchestrationState.duration_seconds
        }
    }
    
    if (Test-Path "$workspaceRoot\scripts\corpus-callosum\send-message.ps1") {
        $messageJson = $coordinationMessage | ConvertTo-Json -Compress
        & "$workspaceRoot\scripts\corpus-callosum\send-message.ps1" -MessageJson $messageJson
    }
    
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host "✅ TDD CYCLE COMPLETE" -ForegroundColor Green
    Write-Host "=" * 80 -ForegroundColor Green
    Write-Host ""
    Write-Host "Feature: $featureName" -ForegroundColor Cyan
    Write-Host "Duration: $([math]::Round($orchestrationState.duration_seconds, 1)) seconds" -ForegroundColor Gray
    Write-Host "All phases: ✅ RED ✅ GREEN ✅ REFACTOR" -ForegroundColor Green
    Write-Host ""
    
    return $orchestrationState
    
} catch {
    $orchestrationState.status = "FAILED"
    $orchestrationState.error_message = $_.Exception.Message
    
    Write-Host "`n❌ TDD Cycle Failed: $($_.Exception.Message)" -ForegroundColor Red
    
    throw
}
