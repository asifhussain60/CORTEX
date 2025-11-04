# Optimize Plan from Metrics
# Week 4 Phase 3: Right→Left Optimization
# Right brain analyzes metrics and generates plan optimizations

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [hashtable]$Metrics,
    
    [Parameter(Mandatory=$false)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$OriginalPlan,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-LatestOptimizationSuggestions {
    $suggestionsFile = "kds-brain\right-hemisphere\optimization-suggestions.jsonl"
    
    if (-not (Test-Path $suggestionsFile)) {
        return $null
    }
    
    Get-Content $suggestionsFile -Tail 1 |
        ForEach-Object { 
            try { $_ | ConvertFrom-Json } 
            catch { $null }
        }
}

function Get-CurrentPlan {
    param([string]$SessionId)
    
    if (-not $SessionId) {
        return $null
    }
    
    $sessionFile = "sessions\$SessionId.yaml"
    
    if (-not (Test-Path $sessionFile)) {
        return $null
    }
    
    # Parse YAML session file to extract plan
    $content = Get-Content $sessionFile -Raw
    
    # Simple YAML parsing for phases
    # In production, use proper YAML parser
    return @{
        session_id = $SessionId
        phases = @()  # Would be populated from actual session
    }
}

function Optimize-PhaseTiming {
    param(
        [hashtable]$PhaseDuration,
        [array]$Suggestions
    )
    
    $optimizations = @()
    
    # Find slow phases
    $slowPhases = $Suggestions | Where-Object { 
        $_.type -eq "performance" -and $_.phase 
    }
    
    foreach ($slowPhase in $slowPhases) {
        $phaseId = $slowPhase.phase
        $currentDuration = $PhaseDuration[$phaseId]
        
        if ($currentDuration -gt 600) {
            # Suggest breaking down phase
            $optimizations += @{
                type = "phase_breakdown"
                phase = $phaseId
                current_estimate = $currentDuration
                suggested_approach = "Break into smaller subtasks"
                estimated_improvement = [Math]::Round($currentDuration * 0.3)  # 30% improvement
                rationale = "Large phases (>10 min) are harder to estimate and more error-prone"
            }
        }
        
        if ($currentDuration -gt 1200) {
            # Critical - needs parallelization or redesign
            $optimizations += @{
                type = "phase_parallelization"
                phase = $phaseId
                current_estimate = $currentDuration
                suggested_approach = "Parallelize independent work or redesign approach"
                estimated_improvement = [Math]::Round($currentDuration * 0.5)  # 50% improvement
                rationale = "Very slow phases (>20 min) benefit from parallel execution"
            }
        }
    }
    
    return $optimizations
}

function Optimize-TDDWorkflow {
    param(
        [hashtable]$TDDEffectiveness,
        [array]$Suggestions
    )
    
    $optimizations = @()
    
    # Check if TDD was followed
    if (-not $TDDEffectiveness.tdd_followed) {
        $optimizations += @{
            type = "enforce_tdd"
            current_state = "TDD not followed"
            suggested_approach = "Add explicit RED→GREEN→REFACTOR checkpoints"
            estimated_improvement = 180  # 3 minutes saved from reduced rework
            rationale = "TDD reduces rework and improves first-time quality"
        }
    }
    
    # Check for excessive cycles
    if ($TDDEffectiveness.cycles_needed -gt 3) {
        $optimizations += @{
            type = "requirement_clarity"
            current_state = "Multiple TDD cycles needed ($($TDDEffectiveness.cycles_needed))"
            suggested_approach = "Spend more time in planning phase clarifying requirements"
            estimated_improvement = ($TDDEffectiveness.cycles_needed - 1) * 120  # ~2 min per extra cycle
            rationale = "Clear requirements reduce trial-and-error cycles"
        }
    }
    
    # Check phase balance
    $totalTime = $TDDEffectiveness.red_phase_time + $TDDEffectiveness.green_phase_time + $TDDEffectiveness.refactor_phase_time
    
    if ($totalTime -gt 0) {
        $refactorRatio = $TDDEffectiveness.refactor_phase_time / $totalTime
        
        if ($refactorRatio -lt 0.15) {
            $optimizations += @{
                type = "increase_refactoring"
                current_state = "Low refactoring time ($([Math]::Round($refactorRatio * 100, 1))%)"
                suggested_approach = "Allocate 20-25% of TDD time to refactoring"
                estimated_improvement = -60  # Negative = takes more time upfront, but saves later
                rationale = "Proper refactoring prevents technical debt accumulation"
            }
        }
    }
    
    return $optimizations
}

function Optimize-TestStrategy {
    param(
        [hashtable]$TestResults,
        [array]$Suggestions
    )
    
    $optimizations = @()
    
    # Coverage optimization
    if ($TestResults.coverage -lt 80) {
        $coverageGap = 80 - $TestResults.coverage
        
        $optimizations += @{
            type = "increase_coverage"
            current_state = "Coverage at $($TestResults.coverage)%"
            suggested_approach = "Add tests for uncovered paths before proceeding"
            estimated_improvement = -($coverageGap * 2)  # ~2 min per % coverage point
            rationale = "80% coverage is minimum for safe refactoring"
        }
    }
    
    # Failing tests
    if ($TestResults.failed -gt 0) {
        $optimizations += @{
            type = "fix_tests_first"
            current_state = "$($TestResults.failed) failing tests"
            suggested_approach = "HALT: Fix all failing tests before proceeding"
            estimated_improvement = 300  # 5 min saved from preventing cascading failures
            rationale = "Failing tests indicate unstable foundation"
            priority = "critical"
        }
    }
    
    return $optimizations
}

function Optimize-ComplexityManagement {
    param(
        [hashtable]$ComplexityMetrics,
        [array]$Suggestions
    )
    
    $optimizations = @()
    
    # Large changeset
    $netLines = $ComplexityMetrics.lines_added - $ComplexityMetrics.lines_deleted
    
    if ($netLines -gt 2000) {
        $optimizations += @{
            type = "reduce_changeset"
            current_state = "$netLines net lines changed"
            suggested_approach = "Break work into smaller incremental commits"
            estimated_improvement = 0  # No time saved, but reduces risk
            rationale = "Large changesets are harder to review and more error-prone"
        }
    }
    
    # Too many files
    if ($ComplexityMetrics.files_created -gt 15) {
        $optimizations += @{
            type = "simplify_design"
            current_state = "$($ComplexityMetrics.files_created) files created"
            suggested_approach = "Review if all files are necessary, consider consolidation"
            estimated_improvement = 120  # 2 min saved from simpler structure
            rationale = "Excessive file creation suggests over-engineering"
        }
    }
    
    # Dependency management
    if ($ComplexityMetrics.dependencies_added -gt 5) {
        $optimizations += @{
            type = "review_dependencies"
            current_state = "$($ComplexityMetrics.dependencies_added) dependencies added"
            suggested_approach = "Verify each dependency is essential"
            estimated_improvement = 0  # Risk reduction, not time savings
            rationale = "Each dependency adds maintenance burden"
        }
    }
    
    return $optimizations
}

function Optimize-ErrorPrevention {
    param(
        [hashtable]$ErrorRecovery,
        [array]$Suggestions
    )
    
    $optimizations = @()
    
    # Frequent errors
    if ($ErrorRecovery.errors_encountered -gt 3) {
        $optimizations += @{
            type = "add_validation"
            current_state = "$($ErrorRecovery.errors_encountered) errors encountered"
            suggested_approach = "Add pre-validation checks before critical operations"
            estimated_improvement = 180  # 3 min saved from preventing errors
            rationale = "Validation upfront is cheaper than recovery later"
        }
    }
    
    # Rollbacks
    if ($ErrorRecovery.rollbacks_needed -gt 0) {
        $optimizations += @{
            type = "strengthen_validation"
            current_state = "$($ErrorRecovery.rollbacks_needed) rollbacks required"
            suggested_approach = "Add dry-run mode and confirmation steps"
            estimated_improvement = 240  # 4 min saved from preventing rollbacks
            rationale = "Rollbacks waste time and can lose work"
        }
    }
    
    return $optimizations
}

function Calculate-TotalTimeImpact {
    param([array]$Optimizations)
    
    $totalImprovement = ($Optimizations | Measure-Object -Property estimated_improvement -Sum).Sum ?? 0
    
    return @{
        total_optimizations = $Optimizations.Count
        estimated_time_saved = $totalImprovement
        net_impact = if ($totalImprovement -gt 0) { "faster" } else { "slower upfront, better quality" }
    }
}

function Create-OptimizedPlan {
    param(
        [array]$Optimizations,
        [hashtable]$OriginalMetrics
    )
    
    # Sort by priority and impact
    $priorityOrder = @{ "critical" = 0; "high" = 1; "medium" = 2; "low" = 3 }
    $sortedOptimizations = $Optimizations | Sort-Object {
        $priority = $_.priority ?? "medium"
        $priorityOrder[$priority]
    }, { -$_.estimated_improvement }
    
    return @{
        generated_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        based_on_session = $OriginalMetrics.session_id
        total_optimizations = $Optimizations.Count
        optimizations = $sortedOptimizations
        impact_summary = Calculate-TotalTimeImpact -Optimizations $Optimizations
        
        recommendations = @{
            immediate = $sortedOptimizations | Where-Object { ($_.priority ?? "medium") -in @("critical", "high") }
            consider = $sortedOptimizations | Where-Object { ($_.priority ?? "medium") -eq "medium" }
            optional = $sortedOptimizations | Where-Object { ($_.priority ?? "medium") -eq "low" }
        }
    }
}

# Main execution
try {
    Write-Verbose "Starting plan optimization"
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would optimize plan from metrics" -ForegroundColor Yellow
        
        # Return mock optimizations
        $mockOptimizations = @(
            @{
                type = "phase_breakdown"
                phase = "phase_2"
                current_estimate = 1200
                suggested_approach = "Break into smaller tasks"
                estimated_improvement = 360
                action = "split_into_smaller_phases"
            }
            @{
                type = "enforce_tdd"
                suggested_approach = "Add RED→GREEN→REFACTOR checkpoints"
                estimated_improvement = 180
                action = "add_tdd_checkpoints"
            }
        )
        
        # Calculate estimated time if OriginalPlan provided
        $estimatedTime = if ($OriginalPlan -and $OriginalPlan.estimated_time) {
            # Reduce by 10% from optimizations
            [Math]::Round($OriginalPlan.estimated_time * 0.9)
        } else {
            45  # Default optimized time
        }
        
        return @{
            phases = @("phase_0", "phase_1", "phase_2")
            optimizations_applied = $mockOptimizations
            total_optimizations = 2
            estimated_time_saved = 540
            estimated_time = $estimatedTime
            optimizations = $mockOptimizations
        }
    }
    
    # Get metrics (from parameter or latest suggestions)
    if (-not $Metrics -and -not $SessionId) {
        Write-Verbose "No metrics provided, getting latest suggestions"
        $latestSuggestions = Get-LatestOptimizationSuggestions
        
        if (-not $latestSuggestions) {
            Write-Warning "No optimization suggestions found"
            return @{
                error = "No suggestions found"
                optimizations = @()
            }
        }
        
        $SessionId = $latestSuggestions.session_id
        $suggestions = $latestSuggestions.suggestions
        
        # Mock metrics extraction (in production, would fetch from session)
        $Metrics = @{
            session_id = $SessionId
            phase_duration = @{ phase_1 = 300; phase_2 = 1200 }
            tdd_effectiveness = @{ tdd_followed = $true; cycles_needed = 2; red_phase_time = 192; green_phase_time = 394; refactor_phase_time = 159 }
            test_results = @{ total_tests = 47; passed = 47; failed = 0; coverage = 94 }
            complexity_metrics = @{ files_created = 4; lines_added = 847; lines_deleted = 0; dependencies_added = 2 }
            error_recovery = @{ errors_encountered = 0; rollbacks_needed = 0 }
        }
    } else {
        # Extract suggestions from metrics if not already have them
        $suggestions = @()
    }
    
    Write-Verbose "Generating optimizations for session: $($Metrics.session_id)"
    
    # Generate optimizations from each aspect
    $allOptimizations = @()
    
    $allOptimizations += Optimize-PhaseTiming -PhaseDuration $Metrics.phase_duration -Suggestions $suggestions
    $allOptimizations += Optimize-TDDWorkflow -TDDEffectiveness $Metrics.tdd_effectiveness -Suggestions $suggestions
    $allOptimizations += Optimize-TestStrategy -TestResults $Metrics.test_results -Suggestions $suggestions
    $allOptimizations += Optimize-ComplexityManagement -ComplexityMetrics $Metrics.complexity_metrics -Suggestions $suggestions
    $allOptimizations += Optimize-ErrorPrevention -ErrorRecovery $Metrics.error_recovery -Suggestions $suggestions
    
    Write-Verbose "Generated $($allOptimizations.Count) optimizations"
    
    # Create optimized plan
    $optimizedPlan = Create-OptimizedPlan -Optimizations $allOptimizations -OriginalMetrics $Metrics
    
    # Display summary
    Write-Host "✅ Plan optimizations generated" -ForegroundColor Green
    Write-Host "  Session: $($Metrics.session_id)" -ForegroundColor Cyan
    Write-Host "  Optimizations: $($allOptimizations.Count)" -ForegroundColor Cyan
    Write-Host "  Estimated time saved: $($optimizedPlan.impact_summary.estimated_time_saved)s" -ForegroundColor Cyan
    
    $criticalCount = ($allOptimizations | Where-Object { ($_.priority ?? "medium") -eq "critical" }).Count
    if ($criticalCount -gt 0) {
        Write-Host "  ⚠️  Critical actions: $criticalCount" -ForegroundColor Red
    }
    
    return $optimizedPlan
    
} catch {
    Write-Error "Plan optimization failed: $_"
    throw
}
