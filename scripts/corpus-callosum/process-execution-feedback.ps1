# Process Execution Feedback
# Week 4 Phase 2: Left→Right Feedback
# Right brain processes execution feedback and generates optimization suggestions

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$MessageId,
    
    [Parameter(Mandatory=$false)]
    [hashtable]$Feedback,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-PendingFeedback {
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
            $_.type -eq "execution_feedback" -and 
            $_.destination -eq "right_hemisphere" -and
            $_.status -eq "pending"
        }
}

function Get-FeedbackById {
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

function Analyze-PhasePerformance {
    param([hashtable]$PhaseDuration)
    
    $suggestions = @()
    
    foreach ($phase in $PhaseDuration.Keys) {
        $duration = $PhaseDuration[$phase]
        
        # Flag slow phases (>10 minutes)
        if ($duration -gt 600) {
            $suggestions += @{
                type = "performance"
                phase = $phase
                severity = "medium"
                issue = "Slow phase execution"
                current_value = $duration
                threshold = 600
                suggestion = "Consider breaking down $phase into smaller subtasks or parallelizing work"
            }
        }
        
        # Flag very slow phases (>20 minutes)
        if ($duration -gt 1200) {
            $suggestions += @{
                type = "performance"
                phase = $phase
                severity = "high"
                issue = "Very slow phase execution"
                current_value = $duration
                threshold = 1200
                suggestion = "Critical: $phase needs significant optimization or redesign"
            }
        }
    }
    
    return $suggestions
}

function Analyze-TDDPractice {
    param([hashtable]$TDDEffectiveness)
    
    $suggestions = @()
    
    # Check if TDD was followed
    if (-not $TDDEffectiveness.tdd_followed) {
        $suggestions += @{
            type = "process"
            severity = "high"
            issue = "TDD not followed"
            suggestion = "Always follow RED→GREEN→REFACTOR cycle for better quality"
        }
    }
    
    # Check for too many cycles (indicates unclear requirements)
    if ($TDDEffectiveness.cycles_needed -gt 3) {
        $suggestions += @{
            type = "process"
            severity = "medium"
            issue = "Multiple TDD cycles needed"
            current_value = $TDDEffectiveness.cycles_needed
            suggestion = "Clarify requirements in planning phase to reduce rework"
        }
    }
    
    # Check phase balance (ideal: RED:GREEN:REFACTOR ~= 1:2:1)
    $totalTime = $TDDEffectiveness.red_phase_time + $TDDEffectiveness.green_phase_time + $TDDEffectiveness.refactor_phase_time
    
    if ($totalTime -gt 0) {
        $redRatio = $TDDEffectiveness.red_phase_time / $totalTime
        $greenRatio = $TDDEffectiveness.green_phase_time / $totalTime
        $refactorRatio = $TDDEffectiveness.refactor_phase_time / $totalTime
        
        # Too much time in RED (writing tests)
        if ($redRatio -gt 0.4) {
            $suggestions += @{
                type = "process"
                severity = "low"
                issue = "High time in RED phase"
                current_value = [Math]::Round($redRatio * 100, 1)
                suggestion = "Consider simpler test cases or better test tooling"
            }
        }
        
        # Too little refactoring
        if ($refactorRatio -lt 0.15) {
            $suggestions += @{
                type = "quality"
                severity = "medium"
                issue = "Insufficient refactoring"
                current_value = [Math]::Round($refactorRatio * 100, 1)
                suggestion = "Invest more time in code cleanup and optimization"
            }
        }
    }
    
    return $suggestions
}

function Analyze-TestCoverage {
    param([hashtable]$TestResults)
    
    $suggestions = @()
    
    # Check for failing tests
    if ($TestResults.failed -gt 0) {
        $suggestions += @{
            type = "quality"
            severity = "critical"
            issue = "Failing tests detected"
            current_value = $TestResults.failed
            suggestion = "Fix all failing tests before proceeding"
        }
    }
    
    # Check coverage
    if ($TestResults.coverage -lt 80) {
        $suggestions += @{
            type = "quality"
            severity = "high"
            issue = "Low test coverage"
            current_value = $TestResults.coverage
            threshold = 80
            suggestion = "Increase test coverage to at least 80%"
        }
    } elseif ($TestResults.coverage -lt 90) {
        $suggestions += @{
            type = "quality"
            severity = "medium"
            issue = "Test coverage could be improved"
            current_value = $TestResults.coverage
            threshold = 90
            suggestion = "Target 90%+ coverage for critical code paths"
        }
    }
    
    return $suggestions
}

function Analyze-Complexity {
    param([hashtable]$ComplexityMetrics)
    
    $suggestions = @()
    
    # Check for excessive file creation
    if ($ComplexityMetrics.files_created -gt 15) {
        $suggestions += @{
            type = "design"
            severity = "medium"
            issue = "High number of files created"
            current_value = $ComplexityMetrics.files_created
            suggestion = "Consider consolidating related functionality"
        }
    }
    
    # Check for large changesets
    $netLines = $ComplexityMetrics.lines_added - $ComplexityMetrics.lines_deleted
    if ($netLines -gt 2000) {
        $suggestions += @{
            type = "process"
            severity = "medium"
            issue = "Large changeset"
            current_value = $netLines
            suggestion = "Break down into smaller, incremental changes"
        }
    }
    
    # Check for dependency growth
    if ($ComplexityMetrics.dependencies_added -gt 5) {
        $suggestions += @{
            type = "design"
            severity = "low"
            issue = "Multiple dependencies added"
            current_value = $ComplexityMetrics.dependencies_added
            suggestion = "Review if all dependencies are necessary"
        }
    }
    
    return $suggestions
}

function Analyze-ErrorPatterns {
    param([hashtable]$ErrorRecovery)
    
    $suggestions = @()
    
    # Check for frequent errors
    if ($ErrorRecovery.errors_encountered -gt 3) {
        $suggestions += @{
            type = "quality"
            severity = "high"
            issue = "Frequent errors encountered"
            current_value = $ErrorRecovery.errors_encountered
            suggestion = "Review error patterns and add preventive checks"
        }
    }
    
    # Check for rollbacks
    if ($ErrorRecovery.rollbacks_needed -gt 0) {
        $suggestions += @{
            type = "process"
            severity = "high"
            issue = "Rollbacks required"
            current_value = $ErrorRecovery.rollbacks_needed
            suggestion = "Improve validation before committing changes"
        }
    }
    
    return $suggestions
}

function Generate-OptimizationSuggestions {
    param([hashtable]$Feedback)
    
    $allSuggestions = @()
    
    # Analyze each aspect
    $allSuggestions += Analyze-PhasePerformance -PhaseDuration $Feedback.phase_duration
    $allSuggestions += Analyze-TDDPractice -TDDEffectiveness $Feedback.tdd_effectiveness
    $allSuggestions += Analyze-TestCoverage -TestResults $Feedback.test_results
    $allSuggestions += Analyze-Complexity -ComplexityMetrics $Feedback.complexity_metrics
    $allSuggestions += Analyze-ErrorPatterns -ErrorRecovery $Feedback.error_recovery
    
    # Sort by severity
    $severityOrder = @{ "critical" = 0; "high" = 1; "medium" = 2; "low" = 3 }
    $allSuggestions = $allSuggestions | Sort-Object { $severityOrder[$_.severity] }
    
    return $allSuggestions
}

function Save-OptimizationSuggestions {
    param(
        [string]$SessionId,
        [array]$Suggestions
    )
    
    $suggestionsFile = "kds-brain\right-hemisphere\optimization-suggestions.jsonl"
    
    # Ensure directory exists
    $suggestionsDir = Split-Path $suggestionsFile -Parent
    if (-not (Test-Path $suggestionsDir)) {
        $null = New-Item $suggestionsDir -ItemType Directory -Force
    }
    
    $record = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        session_id = $SessionId
        suggestion_count = $Suggestions.Count
        critical_count = ($Suggestions | Where-Object { $_.severity -eq "critical" }).Count
        high_count = ($Suggestions | Where-Object { $_.severity -eq "high" }).Count
        suggestions = $Suggestions
    }
    
    $record | ConvertTo-Json -Depth 10 -Compress | Add-Content $suggestionsFile
    
    Write-Verbose "Saved $($Suggestions.Count) optimization suggestions"
}

# Main execution
try {
    Write-Verbose "Starting feedback processing"
    
    # Get feedback message
    if ($Feedback) {
        # Direct feedback provided (for testing)
        $feedbackData = $Feedback
        $sessionId = $Feedback.session_id ?? "test-session"
    } elseif ($MessageId) {
        $feedbackMsg = Get-FeedbackById -Id $MessageId
        if (-not $feedbackMsg) {
            Write-Warning "No feedback message found with ID: $MessageId"
            return @{
                error = "No feedback found"
                processed = $false
            }
        }
        $feedbackData = $feedbackMsg.content
        $sessionId = $feedbackMsg.content.session_id
        Write-Verbose "Processing feedback message: $($feedbackMsg.id)"
    } else {
        $pending = Get-PendingFeedback
        $feedbackMsg = $pending | Select-Object -First 1
        if (-not $feedbackMsg) {
            Write-Warning "No pending feedback found to process"
            return @{
                error = "No feedback found"
                processed = $false
            }
        }
        $feedbackData = $feedbackMsg.content
        $sessionId = $feedbackMsg.content.session_id
        Write-Verbose "Processing feedback message: $($feedbackMsg.id)"
    }
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would process execution feedback" -ForegroundColor Yellow
        
        # Generate mock suggestions
        $suggestions = @(
            @{
                type = "performance"
                severity = "medium"
                issue = "Phase execution time high"
                suggestion = "Consider optimization"
            }
            @{
                type = "quality"
                severity = "high"
                issue = "Test coverage below 90%"
                suggestion = "Add more test cases"
            }
        )
        
        Write-Host "  Suggestions: $($suggestions.Count)" -ForegroundColor Cyan
        
        return $suggestions
    }
    
    # Generate optimization suggestions
    Write-Verbose "Analyzing feedback and generating suggestions"
    $suggestions = Generate-OptimizationSuggestions -Feedback $feedbackData
    
    Write-Verbose "Generated $($suggestions.Count) suggestions"
    
    # Save suggestions
    Save-OptimizationSuggestions -SessionId $sessionId -Suggestions $suggestions
    
    # Display summary
    Write-Host "✅ Feedback processed" -ForegroundColor Green
    Write-Host "  Session: $sessionId" -ForegroundColor Cyan
    Write-Host "  Suggestions: $($suggestions.Count)" -ForegroundColor Cyan
    
    $criticalCount = ($suggestions | Where-Object { $_.severity -eq "critical" }).Count
    $highCount = ($suggestions | Where-Object { $_.severity -eq "high" }).Count
    
    if ($criticalCount -gt 0) {
        Write-Host "  Critical issues: $criticalCount" -ForegroundColor Red
    }
    if ($highCount -gt 0) {
        Write-Host "  High priority: $highCount" -ForegroundColor Yellow
    }
    
    return @{
        message_id = if ($feedbackMsg) { $feedbackMsg.id } else { "direct-feedback" }
        session_id = $sessionId
        suggestions = $suggestions
        critical_count = $criticalCount
        high_count = $highCount
        processed = $true
    }
    
} catch {
    Write-Error "Feedback processing failed: $_"
    throw
}
