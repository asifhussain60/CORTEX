# Collect Execution Metrics
# Week 4 Phase 2: Left→Right Feedback
# Gathers metrics from left brain execution for right brain optimization

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$SessionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-LatestSession {
    $stateFile = "kds-brain\left-hemisphere\execution-state.jsonl"
    
    if (-not (Test-Path $stateFile)) {
        Write-Verbose "No execution state file found"
        return $null
    }
    
    # Get last session from execution state
    $lastEvent = Get-Content $stateFile -Tail 10 |
        ForEach-Object { 
            try { $_ | ConvertFrom-Json } 
            catch { $null }
        } |
        Where-Object { $_.session_id } |
        Select-Object -Last 1
    
    return $lastEvent.session_id
}

function Get-SessionEvents {
    param([string]$SessionId)
    
    $stateFile = "kds-brain\left-hemisphere\execution-state.jsonl"
    
    if (-not (Test-Path $stateFile)) {
        return @()
    }
    
    Get-Content $stateFile |
        ForEach-Object { 
            try { $_ | ConvertFrom-Json } 
            catch { $null }
        } |
        Where-Object { $_.session_id -eq $SessionId }
}

function Measure-PhaseDuration {
    param([array]$Events)
    
    $phaseMetrics = @{}
    
    $phaseEvents = $Events | Where-Object { $_.type -eq "phase_complete" }
    
    foreach ($event in $phaseEvents) {
        $phaseId = $event.phase_id
        $duration = $event.duration_seconds ?? 0
        
        if (-not $phaseMetrics.ContainsKey($phaseId)) {
            $phaseMetrics[$phaseId] = $duration
        }
    }
    
    return $phaseMetrics
}

function Measure-TDDEffectiveness {
    param([array]$Events)
    
    $tddEvents = $Events | Where-Object { 
        $_.type -in @("test_created", "test_run", "code_implemented", "code_refactored") 
    }
    
    $redPhase = $tddEvents | Where-Object { $_.phase -eq "RED" } | Measure-Object -Property duration_seconds -Sum
    $greenPhase = $tddEvents | Where-Object { $_.phase -eq "GREEN" } | Measure-Object -Property duration_seconds -Sum
    $refactorPhase = $tddEvents | Where-Object { $_.phase -eq "REFACTOR" } | Measure-Object -Property duration_seconds -Sum
    
    $cyclesNeeded = ($tddEvents | Where-Object { $_.type -eq "test_run" -and $_.phase -eq "GREEN" }).Count
    
    return @{
        red_phase_time = $redPhase.Sum ?? 0
        green_phase_time = $greenPhase.Sum ?? 0
        refactor_phase_time = $refactorPhase.Sum ?? 0
        cycles_needed = $cyclesNeeded
        tdd_followed = ($redPhase.Count -gt 0 -and $greenPhase.Count -gt 0)
    }
}

function Measure-TestResults {
    param([array]$Events)
    
    $testEvents = $Events | Where-Object { $_.type -eq "test_run" }
    
    if ($testEvents.Count -eq 0) {
        return @{
            total_tests = 0
            passed = 0
            failed = 0
            coverage = 0
        }
    }
    
    $lastTestRun = $testEvents | Select-Object -Last 1
    
    return @{
        total_tests = $lastTestRun.total_tests ?? 0
        passed = $lastTestRun.passed ?? 0
        failed = $lastTestRun.failed ?? 0
        coverage = $lastTestRun.coverage ?? 0
    }
}

function Measure-ComplexityMetrics {
    param([array]$Events)
    
    $fileEvents = $Events | Where-Object { $_.type -in @("file_created", "code_modified") }
    
    $filesCreated = ($fileEvents | Where-Object { $_.type -eq "file_created" }).Count
    $filesModified = ($fileEvents | Where-Object { $_.type -eq "code_modified" }).Count
    
    $linesAdded = ($fileEvents | Measure-Object -Property lines_added -Sum).Sum ?? 0
    $linesDeleted = ($fileEvents | Measure-Object -Property lines_deleted -Sum).Sum ?? 0
    
    $dependencies = $Events | 
        Where-Object { $_.type -eq "dependency_added" } |
        Select-Object -ExpandProperty dependency -Unique |
        Measure-Object |
        Select-Object -ExpandProperty Count
    
    return @{
        files_created = $filesCreated
        files_modified = $filesModified
        lines_added = $linesAdded
        lines_deleted = $linesDeleted
        dependencies_added = $dependencies
    }
}

function Measure-ErrorRecovery {
    param([array]$Events)
    
    $errorEvents = $Events | Where-Object { $_.type -eq "error" }
    $rollbackEvents = $Events | Where-Object { $_.type -eq "rollback" }
    
    return @{
        errors_encountered = $errorEvents.Count
        rollbacks_needed = $rollbackEvents.Count
        error_messages = $errorEvents | Select-Object -ExpandProperty message -First 5
    }
}

function Get-SuccessIndicators {
    param([array]$Events)
    
    $completionEvent = $Events | Where-Object { $_.type -eq "session_complete" } | Select-Object -Last 1
    
    if ($completionEvent) {
        return @{
            session_completed = $true
            all_tests_passed = $completionEvent.all_tests_passed ?? $false
            tdd_followed = $completionEvent.tdd_followed ?? $false
            no_manual_intervention = $completionEvent.no_manual_intervention ?? $false
        }
    }
    
    # Infer from events if no completion event
    $testEvents = $Events | Where-Object { $_.type -eq "test_run" }
    $lastTest = $testEvents | Select-Object -Last 1
    
    return @{
        session_completed = $false
        all_tests_passed = ($lastTest.failed ?? 1) -eq 0
        tdd_followed = ($Events | Where-Object { $_.phase -eq "RED" }).Count -gt 0
        no_manual_intervention = ($Events | Where-Object { $_.type -eq "manual_intervention" }).Count -eq 0
    }
}

# Main execution
try {
    Write-Verbose "Starting execution metrics collection"
    
    if ($WhatIf) {
        Write-Host "⚙️  WhatIf mode: Would collect execution metrics" -ForegroundColor Yellow
        
        # Return mock metrics for testing
        return @{
            phase_duration = @{
                phase_0 = 323
                phase_1 = 765
                phase_2 = 492
            }
            test_results = @{
                total_tests = 47
                passed = 47
                failed = 0
                coverage = 94
            }
            tdd_effectiveness = @{
                red_phase_time = 192
                green_phase_time = 394
                refactor_phase_time = 159
                cycles_needed = 1
            }
            complexity_metrics = @{
                files_created = 4
                lines_added = 847
                dependencies_added = 2
            }
            error_recovery = @{
                errors_encountered = 0
                rollbacks_needed = 0
            }
            success_indicators = @{
                all_tests_passed = $true
                tdd_followed = $true
                no_manual_intervention = $true
            }
        }
    }
    
    # Get session ID (provided or latest)
    if (-not $SessionId) {
        Write-Verbose "No session ID provided, using latest session"
        $SessionId = Get-LatestSession
    }
    
    if (-not $SessionId) {
        Write-Warning "No session found to collect metrics from"
        return @{
            error = "No session found"
            metrics_collected = $false
        }
    }
    
    Write-Verbose "Collecting metrics for session: $SessionId"
    
    # Get all events for this session
    $events = Get-SessionEvents -SessionId $SessionId
    
    if ($events.Count -eq 0) {
        Write-Warning "No events found for session: $SessionId"
        return @{
            error = "No events found"
            session_id = $SessionId
            metrics_collected = $false
        }
    }
    
    Write-Verbose "Processing $($events.Count) events"
    
    # Collect all metrics
    $metrics = @{
        session_id = $SessionId
        collected_at = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
        event_count = $events.Count
        
        phase_duration = Measure-PhaseDuration -Events $events
        tdd_effectiveness = Measure-TDDEffectiveness -Events $events
        test_results = Measure-TestResults -Events $events
        complexity_metrics = Measure-ComplexityMetrics -Events $events
        error_recovery = Measure-ErrorRecovery -Events $events
        success_indicators = Get-SuccessIndicators -Events $events
    }
    
    Write-Verbose "Metrics collected successfully"
    Write-Verbose "  Phases: $($metrics.phase_duration.Count)"
    Write-Verbose "  Tests: $($metrics.test_results.total_tests) total, $($metrics.test_results.passed) passed"
    Write-Verbose "  TDD followed: $($metrics.tdd_effectiveness.tdd_followed)"
    
    return $metrics
    
} catch {
    Write-Error "Execution metrics collection failed: $_"
    throw
}
