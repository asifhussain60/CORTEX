# Apply Plan Optimizations
# Week 4 Phase 3: Right→Left Optimization
# Left brain receives and applies optimization suggestions

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$MessageId,
    
    [Parameter(Mandatory=$false)]
    [array]$Optimizations,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-PendingOptimizations {
    $queueFile = "kds-brain\corpus-callosum\coordination-queue.jsonl"
    
    if (-not (Test-Path $queueFile)) {
        return @()
    }
    
    Get-Content $queueFile |
        ForEach-Object { 
            try { $_ | ConvertFrom-Json } 
            catch { $null }
        } |
        Where-Object { 
            $_.type -eq "plan_optimization" -and 
            $_.destination -eq "left_hemisphere" -and
            $_.status -eq "pending"
        }
}

function Get-OptimizationById {
    param([string]$Id)
    
    $queueFile = "kds-brain\corpus-callosum\coordination-queue.jsonl"
    
    if (-not (Test-Path $queueFile)) {
        return $null
    }
    
    Get-Content $queueFile |
        ForEach-Object { 
            try { $_ | ConvertFrom-Json } 
            catch { $null }
        } |
        Where-Object { $_.id -eq $Id } |
        Select-Object -First 1
}

function Apply-PhaseBreakdown {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying phase breakdown optimization"
    
    return @{
        action = "break_phase_into_subtasks"
        phase = $Optimization.phase
        current_estimate = $Optimization.current_estimate
        new_estimate = $Optimization.current_estimate - $Optimization.estimated_improvement
        subtasks_recommended = [Math]::Ceiling($Optimization.current_estimate / 300)  # ~5 min each
        applied = $true
    }
}

function Apply-PhaseParallelization {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying phase parallelization optimization"
    
    return @{
        action = "parallelize_phase_work"
        phase = $Optimization.phase
        current_estimate = $Optimization.current_estimate
        new_estimate = $Optimization.current_estimate - $Optimization.estimated_improvement
        parallel_streams = 2  # Recommend 2 parallel workstreams
        applied = $true
    }
}

function Apply-EnforceTDD {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying TDD enforcement"
    
    return @{
        action = "add_tdd_checkpoints"
        checkpoints = @("RED: Write failing test", "GREEN: Make test pass", "REFACTOR: Clean up code")
        estimated_time_saved = $Optimization.estimated_improvement
        applied = $true
    }
}

function Apply-RequirementClarity {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying requirement clarity optimization"
    
    return @{
        action = "extend_planning_phase"
        additional_planning_time = 300  # 5 more minutes in planning
        expected_cycle_reduction = 2  # Reduce by 2 cycles
        net_time_saved = $Optimization.estimated_improvement - 300
        applied = $true
    }
}

function Apply-IncreaseRefactoring {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying refactoring increase"
    
    return @{
        action = "allocate_refactor_time"
        target_percentage = 25  # 25% of TDD time
        rationale = "Prevent technical debt"
        applied = $true
    }
}

function Apply-IncreaseCoverage {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying coverage increase"
    
    return @{
        action = "add_coverage_target"
        target_coverage = 80
        current_coverage = $Optimization.current_state -replace '[^\d]', ''
        tests_to_add = [Math]::Ceiling((80 - [int]$Optimization.current_state) / 5)  # ~5% per test
        applied = $true
    }
}

function Apply-FixTestsFirst {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying fix-tests-first optimization"
    
    return @{
        action = "halt_until_tests_pass"
        failing_tests = $Optimization.current_state -replace '[^\d]', ''
        priority = "critical"
        blocking = $true
        applied = $true
    }
}

function Apply-ReduceChangeset {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying changeset reduction"
    
    return @{
        action = "split_into_commits"
        current_size = $Optimization.current_state -replace '[^\d]', ''
        recommended_commits = [Math]::Ceiling([int]($Optimization.current_state -replace '[^\d]', '') / 1000)
        applied = $true
    }
}

function Apply-SimplifyDesign {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying design simplification"
    
    return @{
        action = "review_file_structure"
        files_created = $Optimization.current_state -replace '[^\d]', ''
        suggest_consolidation = $true
        applied = $true
    }
}

function Apply-ReviewDependencies {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying dependency review"
    
    return @{
        action = "validate_dependencies"
        dependencies_added = $Optimization.current_state -replace '[^\d]', ''
        require_justification = $true
        applied = $true
    }
}

function Apply-AddValidation {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying validation addition"
    
    return @{
        action = "add_prevalidation_checks"
        errors_encountered = $Optimization.current_state -replace '[^\d]', ''
        checks_to_add = @("Input validation", "State verification", "Dependency check")
        applied = $true
    }
}

function Apply-StrengthenValidation {
    param([hashtable]$Optimization)
    
    Write-Verbose "Applying validation strengthening"
    
    return @{
        action = "add_dryrun_mode"
        rollbacks_prevented = $Optimization.current_state -replace '[^\d]', ''
        add_confirmation_steps = $true
        applied = $true
    }
}

function Apply-Optimization {
    param([hashtable]$Optimization)
    
    switch ($Optimization.type) {
        "phase_breakdown" { return Apply-PhaseBreakdown -Optimization $Optimization }
        "phase_parallelization" { return Apply-PhaseParallelization -Optimization $Optimization }
        "enforce_tdd" { return Apply-EnforceTDD -Optimization $Optimization }
        "requirement_clarity" { return Apply-RequirementClarity -Optimization $Optimization }
        "increase_refactoring" { return Apply-IncreaseRefactoring -Optimization $Optimization }
        "increase_coverage" { return Apply-IncreaseCoverage -Optimization $Optimization }
        "fix_tests_first" { return Apply-FixTestsFirst -Optimization $Optimization }
        "reduce_changeset" { return Apply-ReduceChangeset -Optimization $Optimization }
        "simplify_design" { return Apply-SimplifyDesign -Optimization $Optimization }
        "review_dependencies" { return Apply-ReviewDependencies -Optimization $Optimization }
        "add_validation" { return Apply-AddValidation -Optimization $Optimization }
        "strengthen_validation" { return Apply-StrengthenValidation -Optimization $Optimization }
        default {
            Write-Warning "Unknown optimization type: $($Optimization.type)"
            return @{ action = "unknown"; applied = $false }
        }
    }
}

function Save-AppliedOptimizations {
    param(
        [string]$SessionId,
        [array]$Applied
    )
    
    $appliedFile = "kds-brain\left-hemisphere\applied-optimizations.jsonl"
    
    # Ensure directory exists
    $appliedDir = Split-Path $appliedFile -Parent
    if (-not (Test-Path $appliedDir)) {
        $null = New-Item $appliedDir -ItemType Directory -Force
    }
    
    $record = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        session_id = $SessionId
        optimizations_applied = $Applied.Count
        applied = $Applied
    }
    
    $record | ConvertTo-Json -Depth 10 -Compress | Add-Content $appliedFile
    
    Write-Verbose "Saved $($Applied.Count) applied optimizations"
}

# Main execution
try {
    Write-Verbose "Starting optimization application"
    
    # Get optimizations (from parameter, message, or queue)
    if ($Optimizations -and $Optimizations.Count -gt 0) {
        # Direct optimizations provided as array
        $optimizationData = @{
            session_id = "direct"
            total_optimizations = $Optimizations.Count
            optimizations = $Optimizations
        }
        $sessionId = "direct"
    } elseif ($MessageId) {
        $message = Get-OptimizationById -Id $MessageId
        if (-not $message) {
            Write-Warning "No optimization message found with ID: $MessageId"
            return @{
                error = "No message found"
                applied = $false
            }
        }
        $optimizationData = $message.content
        $sessionId = $message.content.session_id
    } else {
        $pending = Get-PendingOptimizations
        $message = $pending | Select-Object -First 1
        if (-not $message) {
            Write-Warning "No pending optimizations found"
            return @{
                error = "No optimizations found"
                applied = $false
            }
        }
        $optimizationData = $message.content
        $sessionId = $message.content.session_id
    }
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would apply optimizations" -ForegroundColor Yellow
        
        $mockApplied = @(
            @{ action = "break_phase_into_subtasks"; applied = $true }
            @{ action = "add_tdd_checkpoints"; applied = $true }
        )
        
        Write-Host "  Applied: $($mockApplied.Count)" -ForegroundColor Cyan
        
        return @{
            applied_count = $mockApplied.Count
            applied = $mockApplied
            success = $true
        }
    }
    
    # Apply each optimization
    Write-Verbose "Applying $($optimizationData.total_optimizations) optimizations"
    
    $appliedResults = @()
    
    foreach ($optimization in $optimizationData.optimizations) {
        $result = Apply-Optimization -Optimization $optimization
        $appliedResults += $result
    }
    
    # Save results
    Save-AppliedOptimizations -SessionId $sessionId -Applied $appliedResults
    
    # Calculate summary
    $successCount = ($appliedResults | Where-Object { $_.applied }).Count
    
    Write-Host "✅ Optimizations applied" -ForegroundColor Green
    Write-Host "  Session: $sessionId" -ForegroundColor Cyan
    Write-Host "  Applied: $successCount/$($appliedResults.Count)" -ForegroundColor Cyan
    
    return @{
        session_id = $sessionId
        applied_count = $successCount
        total_optimizations = $appliedResults.Count
        applied = $appliedResults
        success = $true
    }
    
} catch {
    Write-Error "Optimization application failed: $_"
    throw
}
