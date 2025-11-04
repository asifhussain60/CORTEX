# KDS v6.0 Week 2 Validation Test Suite
# Purpose: Validate Left Brain TDD Automation (RED→GREEN→REFACTOR)
#
# Tests MUST fail until Week 2 implementation is complete
# These tests define the acceptance criteria for Week 2

# Note: Removed -Verbose parameter to avoid conflicts with called scripts
# Test output is always verbose by default

$ErrorActionPreference = "Stop"
$script:TestsRun = 0
$script:TestsPassed = 0
$script:TestsFailed = 0

function Test-Assert {
    param(
        [string]$TestName,
        [bool]$Condition,
        [string]$ErrorMessage = "Test failed"
    )
    
    $script:TestsRun++
    
    if ($Condition) {
        Write-Host "  ✅ $TestName" -ForegroundColor Green
        $script:TestsPassed++
    } else {
        Write-Host "  ❌ $TestName - $ErrorMessage" -ForegroundColor Red
        $script:TestsFailed++
    }
}

Write-Host "`n🧪 KDS v6.0 Week 2 Validation Test Suite" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Testing: Left Brain TDD Automation (RED→GREEN→REFACTOR)" -ForegroundColor Yellow
Write-Host ""

$workspaceRoot = "D:\PROJECTS\KDS"

# ============================================================================
# TEST GROUP 1: Test Infrastructure Files (Phase 0)
# ============================================================================
Write-Host "`n📦 Test Group 1: Test Infrastructure Files (7 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Week 2 validation test suite exists" `
    -Condition (Test-Path "$workspaceRoot\tests\v6-progressive\week2-validation.ps1") `
    -ErrorMessage "This file should exist"

Test-Assert `
    -TestName "Test fixtures directory exists" `
    -Condition (Test-Path "$workspaceRoot\tests\fixtures\tdd-cycle") `
    -ErrorMessage "Test fixtures directory missing"

Test-Assert `
    -TestName "Sample feature config fixture exists" `
    -Condition (Test-Path "$workspaceRoot\tests\fixtures\tdd-cycle\sample-feature.yaml") `
    -ErrorMessage "Sample feature config missing"

Test-Assert `
    -TestName "Sample test fixture exists" `
    -Condition (Test-Path "$workspaceRoot\tests\fixtures\tdd-cycle\sample-tests.ps1") `
    -ErrorMessage "Sample test fixture missing"

Test-Assert `
    -TestName "TDD execution state schema exists" `
    -Condition (Test-Path "$workspaceRoot\kds-brain\left-hemisphere\schemas\tdd-execution-state.schema.json") `
    -ErrorMessage "TDD execution state schema missing"

# Validate schema structure
if (Test-Path "$workspaceRoot\kds-brain\left-hemisphere\schemas\tdd-execution-state.schema.json") {
    $schema = Get-Content "$workspaceRoot\kds-brain\left-hemisphere\schemas\tdd-execution-state.schema.json" -Raw | ConvertFrom-Json
    
    Test-Assert `
        -TestName "TDD schema defines required phases" `
        -Condition ($schema.required -contains "phase" -and $schema.required -contains "status") `
        -ErrorMessage "Schema must define phase and status as required"
    
    Test-Assert `
        -TestName "TDD schema defines phase enum (RED, GREEN, REFACTOR)" `
        -Condition ($schema.properties.phase.enum -contains "RED" -and $schema.properties.phase.enum -contains "GREEN" -and $schema.properties.phase.enum -contains "REFACTOR") `
        -ErrorMessage "Schema must define RED, GREEN, REFACTOR phases"
} else {
    Test-Assert -TestName "TDD schema defines required phases" -Condition $false -ErrorMessage "Schema file missing"
    Test-Assert -TestName "TDD schema defines phase enum (RED, GREEN, REFACTOR)" -Condition $false -ErrorMessage "Schema file missing"
}

# ============================================================================
# TEST GROUP 2: RED Phase Automation Scripts (8 tests)
# ============================================================================
Write-Host "`n🔴 Test Group 2: RED Phase Automation Scripts (8 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Test creation script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\create-tests.ps1") `
    -ErrorMessage "create-tests.ps1 missing"

Test-Assert `
    -TestName "Test execution script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\execute-tests.ps1") `
    -ErrorMessage "execute-tests.ps1 missing"

Test-Assert `
    -TestName "RED phase verification script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\verify-red-phase.ps1") `
    -ErrorMessage "verify-red-phase.ps1 missing"

# Test RED phase automation functionality (if scripts exist)
if ((Test-Path "$workspaceRoot\scripts\left-brain\create-tests.ps1") -and 
    (Test-Path "$workspaceRoot\tests\fixtures\tdd-cycle\sample-feature.yaml")) {
    
    try {
        # Run test creation (without -Verbose to avoid parameter conflict)
        $testCreation = & "$workspaceRoot\scripts\left-brain\create-tests.ps1" `
            -FeatureConfig "$workspaceRoot\tests\fixtures\tdd-cycle\sample-feature.yaml" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Test creation script produces test files" `
            -Condition ($testCreation.tests_created -eq $true) `
            -ErrorMessage "Script should create test files"
        
        Test-Assert `
            -TestName "Test creation logs to execution state" `
            -Condition ($testCreation.logged_to_execution_state -eq $true) `
            -ErrorMessage "Script should log to execution-state.jsonl"
        
        Test-Assert `
            -TestName "Test creation returns RED phase status" `
            -Condition ($testCreation.phase -eq "RED") `
            -ErrorMessage "Should return RED phase"
        
    } catch {
        Test-Assert -TestName "Test creation script produces test files" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Test creation logs to execution state" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Test creation returns RED phase status" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Test creation script produces test files" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Test creation logs to execution state" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Test creation returns RED phase status" -Condition $false -ErrorMessage "Prerequisites missing"
}

# Test RED phase verification (if scripts exist)
if ((Test-Path "$workspaceRoot\scripts\left-brain\verify-red-phase.ps1") -and
    (Test-Path "$workspaceRoot\scripts\left-brain\execute-tests.ps1")) {
    
    try {
        $redVerification = & "$workspaceRoot\scripts\left-brain\verify-red-phase.ps1" `
            -TestFile "$workspaceRoot\tests\fixtures\tdd-cycle\sample-tests.ps1" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "RED phase verification confirms tests fail initially" `
            -Condition ($redVerification.tests_failed -eq $true) `
            -ErrorMessage "Tests should fail in RED phase"
        
        Test-Assert `
            -TestName "RED phase verification logs failure to execution state" `
            -Condition ($redVerification.logged_failure -eq $true) `
            -ErrorMessage "Should log test failures"
        
    } catch {
        Test-Assert -TestName "RED phase verification confirms tests fail initially" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "RED phase verification logs failure to execution state" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "RED phase verification confirms tests fail initially" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "RED phase verification logs failure to execution state" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 3: GREEN Phase Automation Scripts (8 tests)
# ============================================================================
Write-Host "`n🟢 Test Group 3: GREEN Phase Automation Scripts (8 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Code implementation script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\implement-code.ps1") `
    -ErrorMessage "implement-code.ps1 missing"

Test-Assert `
    -TestName "Auto test runner script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\auto-test-runner.ps1") `
    -ErrorMessage "auto-test-runner.ps1 missing"

Test-Assert `
    -TestName "GREEN phase verification script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\verify-green-phase.ps1") `
    -ErrorMessage "verify-green-phase.ps1 missing"

# Test GREEN phase automation functionality
if ((Test-Path "$workspaceRoot\scripts\left-brain\implement-code.ps1") -and
    (Test-Path "$workspaceRoot\tests\fixtures\tdd-cycle\sample-feature.yaml")) {
    
    try {
        $codeImpl = & "$workspaceRoot\scripts\left-brain\implement-code.ps1" `
            -FeatureConfig "$workspaceRoot\tests\fixtures\tdd-cycle\sample-feature.yaml" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Code implementation script creates implementation files" `
            -Condition ($codeImpl.code_created -eq $true) `
            -ErrorMessage "Should create implementation files"
        
        Test-Assert `
            -TestName "Code implementation logs to execution state" `
            -Condition ($codeImpl.logged_to_execution_state -eq $true) `
            -ErrorMessage "Should log to execution-state.jsonl"
        
        Test-Assert `
            -TestName "Code implementation returns GREEN phase status" `
            -Condition ($codeImpl.phase -eq "GREEN") `
            -ErrorMessage "Should return GREEN phase"
        
    } catch {
        Test-Assert -TestName "Code implementation script creates implementation files" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Code implementation logs to execution state" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Code implementation returns GREEN phase status" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Code implementation script creates implementation files" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Code implementation logs to execution state" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Code implementation returns GREEN phase status" -Condition $false -ErrorMessage "Prerequisites missing"
}

# Test auto test runner
if (Test-Path "$workspaceRoot\scripts\left-brain\auto-test-runner.ps1") {
    try {
        $autoTest = & "$workspaceRoot\scripts\left-brain\auto-test-runner.ps1" `
            -TestFile "$workspaceRoot\tests\fixtures\tdd-cycle\sample-tests.ps1" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Auto test runner executes tests after code change" `
            -Condition ($autoTest.tests_executed -eq $true) `
            -ErrorMessage "Should execute tests automatically"
        
        Test-Assert `
            -TestName "Auto test runner validates GREEN phase (tests pass)" `
            -Condition ($autoTest.validates_green_phase -eq $true) `
            -ErrorMessage "Should validate tests pass"
        
    } catch {
        Test-Assert -TestName "Auto test runner executes tests after code change" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Auto test runner validates GREEN phase (tests pass)" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Auto test runner executes tests after code change" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Auto test runner validates GREEN phase (tests pass)" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 4: REFACTOR Phase Automation Scripts (7 tests)
# ============================================================================
Write-Host "`n🔵 Test Group 4: REFACTOR Phase Automation Scripts (7 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Refactoring script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\refactor-code.ps1") `
    -ErrorMessage "refactor-code.ps1 missing"

Test-Assert `
    -TestName "Quality checks script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\quality-checks.ps1") `
    -ErrorMessage "quality-checks.ps1 missing"

Test-Assert `
    -TestName "Refactor safety verification script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\verify-refactor-safety.ps1") `
    -ErrorMessage "verify-refactor-safety.ps1 missing"

# Test REFACTOR phase automation
if (Test-Path "$workspaceRoot\scripts\left-brain\refactor-code.ps1") {
    try {
        $refactor = & "$workspaceRoot\scripts\left-brain\refactor-code.ps1" `
            -File "$workspaceRoot\tests\fixtures\tdd-cycle\sample-implementation.cs" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Refactoring script optimizes code" `
            -Condition ($refactor.code_optimized -eq $true) `
            -ErrorMessage "Should optimize code"
        
        Test-Assert `
            -TestName "Refactoring maintains test coverage" `
            -Condition ($refactor.tests_still_pass -eq $true) `
            -ErrorMessage "Tests should still pass after refactor"
        
        Test-Assert `
            -TestName "Refactoring logs to execution state" `
            -Condition ($refactor.logged_to_execution_state -eq $true) `
            -ErrorMessage "Should log to execution-state.jsonl"
        
        Test-Assert `
            -TestName "Refactoring returns REFACTOR phase status" `
            -Condition ($refactor.phase -eq "REFACTOR") `
            -ErrorMessage "Should return REFACTOR phase"
        
    } catch {
        Test-Assert -TestName "Refactoring script optimizes code" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Refactoring maintains test coverage" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Refactoring logs to execution state" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Refactoring returns REFACTOR phase status" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Refactoring script optimizes code" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Refactoring maintains test coverage" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Refactoring logs to execution state" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Refactoring returns REFACTOR phase status" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 5: Validation & Rollback System (7 tests)
# ============================================================================
Write-Host "`n⚠️  Test Group 5: Validation & Rollback System (7 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "Validation automation script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\validate-implementation.ps1") `
    -ErrorMessage "validate-implementation.ps1 missing"

Test-Assert `
    -TestName "Rollback script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\rollback-changes.ps1") `
    -ErrorMessage "rollback-changes.ps1 missing"

# Test validation detects broken tests
if (Test-Path "$workspaceRoot\scripts\left-brain\validate-implementation.ps1") {
    try {
        $validation = & "$workspaceRoot\scripts\left-brain\validate-implementation.ps1" `
            -TestFile "$workspaceRoot\tests\fixtures\tdd-cycle\sample-tests.ps1" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Validation detects test failures" `
            -Condition ($validation.can_detect_failures -eq $true) `
            -ErrorMessage "Should detect when tests fail"
        
        Test-Assert `
            -TestName "Validation triggers rollback on failure" `
            -Condition ($validation.triggers_rollback -eq $true) `
            -ErrorMessage "Should trigger rollback when tests fail"
        
    } catch {
        Test-Assert -TestName "Validation detects test failures" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Validation triggers rollback on failure" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Validation detects test failures" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Validation triggers rollback on failure" -Condition $false -ErrorMessage "Prerequisites missing"
}

# Test rollback mechanism
if (Test-Path "$workspaceRoot\scripts\left-brain\rollback-changes.ps1") {
    try {
        $rollback = & "$workspaceRoot\scripts\left-brain\rollback-changes.ps1" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "Rollback uses Git to revert changes" `
            -Condition ($rollback.uses_git -eq $true) `
            -ErrorMessage "Should use Git for rollback"
        
        Test-Assert `
            -TestName "Rollback tracks rollback points in execution state" `
            -Condition ($rollback.tracks_rollback_points -eq $true) `
            -ErrorMessage "Should track rollback points"
        
        Test-Assert `
            -TestName "Rollback logs rollback events" `
            -Condition ($rollback.logs_rollback_events -eq $true) `
            -ErrorMessage "Should log rollback events to execution state"
        
    } catch {
        Test-Assert -TestName "Rollback uses Git to revert changes" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "Rollback tracks rollback points in execution state" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "Rollback logs rollback events" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "Rollback uses Git to revert changes" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Rollback tracks rollback points in execution state" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "Rollback logs rollback events" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 6: Full TDD Cycle Integration (6 tests)
# ============================================================================
Write-Host "`n🔄 Test Group 6: Full TDD Cycle Integration (6 tests)" -ForegroundColor Cyan

Test-Assert `
    -TestName "TDD cycle orchestrator script exists" `
    -Condition (Test-Path "$workspaceRoot\scripts\left-brain\run-tdd-cycle.ps1") `
    -ErrorMessage "run-tdd-cycle.ps1 missing"

# Test full TDD cycle orchestration
if ((Test-Path "$workspaceRoot\scripts\left-brain\run-tdd-cycle.ps1") -and
    (Test-Path "$workspaceRoot\tests\fixtures\tdd-cycle\sample-feature.yaml")) {
    
    try {
        $fullCycle = & "$workspaceRoot\scripts\left-brain\run-tdd-cycle.ps1" `
            -FeatureConfig "$workspaceRoot\tests\fixtures\tdd-cycle\sample-feature.yaml" `
            -DryRun 2>$null
        
        Test-Assert `
            -TestName "TDD orchestrator executes RED phase" `
            -Condition ($fullCycle.executed_red -eq $true) `
            -ErrorMessage "Should execute RED phase"
        
        Test-Assert `
            -TestName "TDD orchestrator executes GREEN phase" `
            -Condition ($fullCycle.executed_green -eq $true) `
            -ErrorMessage "Should execute GREEN phase"
        
        Test-Assert `
            -TestName "TDD orchestrator executes REFACTOR phase" `
            -Condition ($fullCycle.executed_refactor -eq $true) `
            -ErrorMessage "Should execute REFACTOR phase"
        
        Test-Assert `
            -TestName "TDD orchestrator logs all phases to execution state" `
            -Condition ($fullCycle.all_phases_logged -eq $true) `
            -ErrorMessage "Should log all phases to execution-state.jsonl"
        
        Test-Assert `
            -TestName "TDD orchestrator completes successfully" `
            -Condition ($fullCycle.status -eq "COMPLETE") `
            -ErrorMessage "Should complete full cycle successfully"
        
    } catch {
        Test-Assert -TestName "TDD orchestrator executes RED phase" -Condition $false -ErrorMessage $_.Exception.Message
        Test-Assert -TestName "TDD orchestrator executes GREEN phase" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "TDD orchestrator executes REFACTOR phase" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "TDD orchestrator logs all phases to execution state" -Condition $false -ErrorMessage "Script execution failed"
        Test-Assert -TestName "TDD orchestrator completes successfully" -Condition $false -ErrorMessage "Script execution failed"
    }
} else {
    Test-Assert -TestName "TDD orchestrator executes RED phase" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "TDD orchestrator executes GREEN phase" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "TDD orchestrator executes REFACTOR phase" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "TDD orchestrator logs all phases to execution state" -Condition $false -ErrorMessage "Prerequisites missing"
    Test-Assert -TestName "TDD orchestrator completes successfully" -Condition $false -ErrorMessage "Prerequisites missing"
}

# ============================================================================
# TEST GROUP 7: Code Executor Integration (5 tests)
# ============================================================================
Write-Host "`n🤖 Test Group 7: Code Executor Integration (5 tests)" -ForegroundColor Cyan

# Test code-executor.md has TDD workflow
if (Test-Path "$workspaceRoot\prompts\internal\code-executor.md") {
    $codeExecutor = Get-Content "$workspaceRoot\prompts\internal\code-executor.md" -Raw
    
    Test-Assert `
        -TestName "code-executor.md references TDD cycle workflow" `
        -Condition ($codeExecutor -match "TDD|run-tdd-cycle") `
        -ErrorMessage "code-executor should reference TDD cycle"
    
    Test-Assert `
        -TestName "code-executor.md documents RED→GREEN→REFACTOR" `
        -Condition ($codeExecutor -match "RED.*GREEN.*REFACTOR") `
        -ErrorMessage "Should document TDD phases"
    
    Test-Assert `
        -TestName "code-executor.md logs to left-hemisphere execution state" `
        -Condition ($codeExecutor -match "left-hemisphere.*execution-state") `
            -ErrorMessage "Should log to execution-state.jsonl"
    
    Test-Assert `
        -TestName "code-executor.md sends coordination messages to RIGHT" `
        -Condition ($codeExecutor -match "corpus-callosum|coordination|RIGHT|right-hemisphere") `
        -ErrorMessage "Should coordinate with RIGHT hemisphere"
    
    Test-Assert `
        -TestName "code-executor.md integrates rollback on failure" `
        -Condition ($codeExecutor -match "rollback|revert") `
        -ErrorMessage "Should integrate rollback mechanism"
    
} else {
    Test-Assert -TestName "code-executor.md references TDD cycle workflow" -Condition $false -ErrorMessage "code-executor.md missing"
    Test-Assert -TestName "code-executor.md documents RED→GREEN→REFACTOR" -Condition $false -ErrorMessage "code-executor.md missing"
    Test-Assert -TestName "code-executor.md logs to left-hemisphere execution state" -Condition $false -ErrorMessage "code-executor.md missing"
    Test-Assert -TestName "code-executor.md sends coordination messages to RIGHT" -Condition $false -ErrorMessage "code-executor.md missing"
    Test-Assert -TestName "code-executor.md integrates rollback on failure" -Condition $false -ErrorMessage "code-executor.md missing"
}

# ============================================================================
# TEST GROUP 8: Week 2 Capability Validation (4 tests)
# ============================================================================
Write-Host "`n🎯 Test Group 8: Week 2 Capability Validation (4 tests)" -ForegroundColor Cyan

# These tests validate that Week 2 capabilities work end-to-end
# They will fail until all Week 2 implementation is complete

Test-Assert `
    -TestName "Brain can run TDD cycle automatically" `
    -Condition $false `
    -ErrorMessage "Week 2 not complete - TDD automation not implemented"

Test-Assert `
    -TestName "Brain validates code before committing" `
    -Condition $false `
    -ErrorMessage "Week 2 not complete - validation not implemented"

Test-Assert `
    -TestName "Brain rolls back on test failure" `
    -Condition $false `
    -ErrorMessage "Week 2 not complete - rollback not implemented"

Test-Assert `
    -TestName "Brain can help implement Week 3 using TDD" `
    -Condition $false `
    -ErrorMessage "Week 2 not complete - cannot validate Week 3 readiness yet"

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
Write-Host "📊 WEEK 2 VALIDATION TEST RESULTS" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""
Write-Host "Total Tests Run:    $script:TestsRun" -ForegroundColor White
Write-Host "Tests Passed:       $script:TestsPassed" -ForegroundColor Green
Write-Host "Tests Failed:       $script:TestsFailed" -ForegroundColor Red
Write-Host ""

$passRate = if ($script:TestsRun -gt 0) { 
    [math]::Round(($script:TestsPassed / $script:TestsRun) * 100, 1) 
} else { 
    0 
}

Write-Host "Pass Rate:          $passRate%" -ForegroundColor $(if ($passRate -eq 100) { "Green" } else { "Yellow" })
Write-Host ""

if ($script:TestsFailed -eq 0) {
    Write-Host "✅ ALL WEEK 2 TESTS PASSING - Week 2 Implementation Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Week 2 Capabilities Validated:" -ForegroundColor Cyan
    Write-Host "  - Automated RED→GREEN→REFACTOR TDD cycle" -ForegroundColor Green
    Write-Host "  - Test creation and execution framework" -ForegroundColor Green
    Write-Host "  - Code validation and rollback system" -ForegroundColor Green
    Write-Host "  - Full integration with code-executor.md" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Ready for Week 3: Pattern Matching Implementation" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠️  WEEK 2 IMPLEMENTATION IN PROGRESS" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Expected: All tests should fail until Week 2 is complete" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Create test fixtures (Phase 0)" -ForegroundColor White
    Write-Host "  2. Implement RED phase automation" -ForegroundColor White
    Write-Host "  3. Implement GREEN phase automation" -ForegroundColor White
    Write-Host "  4. Implement REFACTOR phase automation" -ForegroundColor White
    Write-Host "  5. Implement validation & rollback" -ForegroundColor White
    Write-Host "  6. Integrate with code-executor.md" -ForegroundColor White
    Write-Host "  7. Re-run this test suite" -ForegroundColor White
    Write-Host ""
    exit 1
}
