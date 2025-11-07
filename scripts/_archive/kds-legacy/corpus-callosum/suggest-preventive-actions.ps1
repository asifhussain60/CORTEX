# Suggest Preventive Actions
# Week 4 Phase 5: Proactive Intelligence
# Recommends actions to prevent predicted issues

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [array]$Predictions,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$actions = @()

if ($WhatIf) {
    Write-Host "⚙️  WhatIf mode: Would suggest preventive actions" -ForegroundColor Yellow
    return @(
        @{
            action = "add_comprehensive_tests"
            priority = "high"
            rationale = "File instability requires extra validation"
        }
    )
}

# ============================================================================
# Generate Actions from Predictions
# ============================================================================
foreach ($prediction in $Predictions) {
    switch ($prediction.type) {
        "file_hotspot" {
            $actions += @{
                action = "add_comprehensive_tests"
                file = $prediction.file
                priority = "high"
                rationale = "High churn rate ($([math]::Round($prediction.churn_rate * 100))%) indicates instability"
                steps = @(
                    "Create unit tests for modified methods"
                    "Add integration tests for file interactions"
                    "Run existing test suite before changes"
                    "Consider refactoring to reduce complexity"
                )
            }
            
            $actions += @{
                action = "increase_test_coverage"
                file = $prediction.file
                priority = "medium"
                rationale = "Unstable files need better test coverage"
                steps = @(
                    "Review current test coverage"
                    "Identify untested code paths"
                    "Add tests for edge cases"
                )
            }
        }
        
        "complexity" {
            $actions += @{
                action = "use_phased_approach"
                feature = $prediction.feature
                priority = "high"
                rationale = "Complex features benefit from incremental implementation"
                steps = @(
                    "Break feature into smaller phases"
                    "Implement core functionality first"
                    "Add integrations incrementally"
                    "Test each phase before proceeding"
                )
            }
            
            $actions += @{
                action = "add_error_handling"
                feature = $prediction.feature
                priority = "medium"
                rationale = "External integrations need robust error handling"
                steps = @(
                    "Plan for service unavailability"
                    "Add retry logic with exponential backoff"
                    "Implement fallback behavior"
                    "Log errors for monitoring"
                )
            }
        }
        
        "historical" {
            $actions += @{
                action = "review_patterns"
                priority = "low"
                rationale = "Learn from previous similar implementations"
                steps = @(
                    "Review knowledge graph for similar features"
                    "Identify common pitfalls"
                    "Apply successful patterns"
                    "Avoid known anti-patterns"
                )
            }
        }
    }
}

# ============================================================================
# Deduplicate and Prioritize
# ============================================================================
$uniqueActions = @{}
foreach ($action in $actions) {
    $key = $action.action
    if (-not $uniqueActions.ContainsKey($key)) {
        $uniqueActions[$key] = $action
    }
}

$sortedActions = $uniqueActions.Values | Sort-Object @{Expression={
    switch ($_.priority) {
        "high" { 1 }
        "medium" { 2 }
        "low" { 3 }
        default { 4 }
    }
}}

# ============================================================================
# Display Actions
# ============================================================================
if ($sortedActions.Count -gt 0) {
    Write-Host "`n💡 Preventive Actions Recommended:" -ForegroundColor Cyan
    
    foreach ($action in $sortedActions) {
        $color = switch ($action.priority) {
            "high" { "Yellow" }
            "medium" { "Cyan" }
            "low" { "Gray" }
            default { "White" }
        }
        
        Write-Host "`n  [$($action.priority.ToUpper())] $($action.action)" -ForegroundColor $color
        Write-Host "    📋 Rationale: $($action.rationale)" -ForegroundColor Gray
        
        if ($action.steps) {
            Write-Host "    📝 Steps:" -ForegroundColor Gray
            foreach ($step in $action.steps) {
                Write-Host "      - $step" -ForegroundColor DarkGray
            }
        }
    }
}

return $sortedActions
