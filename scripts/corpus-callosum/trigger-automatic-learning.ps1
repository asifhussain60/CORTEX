# Trigger Automatic Learning
# Week 4 Phase 4: Continuous Learning Automation
# Determines when to run the learning cycle

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("task_completion", "time_threshold", "event_threshold", "manual")]
    [string]$Trigger = "task_completion",
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$result = @{
    learning_pipeline_invoked = $false
    trigger_type = $Trigger
    reason = ""
    timestamp = (Get-Date).ToString("o")
}

# ============================================================================
# Check if learning should be triggered
# ============================================================================
function Test-ShouldTriggerLearning {
    param(
        [string]$TriggerType,
        [bool]$IsWhatIf
    )
    
    switch ($TriggerType) {
        "task_completion" {
            # In WhatIf mode, simulate a task completion for testing
            if ($IsWhatIf) {
                return @{ should_trigger = $true; reason = "WhatIf: Simulated task completion" }
            }
            
            # Check if a task just completed
            $executionState = "kds-brain\left-hemisphere\execution-state.jsonl"
            if (Test-Path $executionState) {
                $lastEvent = Get-Content $executionState |
                    Where-Object { $_ -and -not $_.TrimStart().StartsWith('#') } |
                    Select-Object -Last 1 |
                    ConvertFrom-Json -ErrorAction SilentlyContinue
                
                if ($lastEvent -and $lastEvent.phase_status -eq "completed") {
                    return @{ should_trigger = $true; reason = "Task phase completed" }
                }
            }
            return @{ should_trigger = $false; reason = "No recent task completion" }
        }
        
        "event_threshold" {
            # Check event count
            $eventsFile = "kds-brain\events.jsonl"
            if (Test-Path $eventsFile) {
                $lastUpdate = Get-Content "kds-brain\knowledge-graph.yaml" -Raw -ErrorAction SilentlyContinue
                if ($lastUpdate -and $lastUpdate -match "last_updated:\s*[`"']?(.+?)[`"']?\s*$") {
                    try {
                        $lastUpdateTime = [DateTime]::Parse($matches[1].Trim())
                        $eventsFileObj = Get-Item $eventsFile
                        $newEvents = (Get-Content $eventsFileObj.FullName | 
                            ForEach-Object { 
                                try {
                                    $_ | ConvertFrom-Json -ErrorAction Stop 
                                } catch {
                                    $null
                                }
                            } |
                            Where-Object { $_ -ne $null -and $_.timestamp -and (Get-Date $_.timestamp) -gt $lastUpdateTime } |
                            Measure-Object).Count
                        
                        if ($newEvents -ge 50) {
                            return @{ should_trigger = $true; reason = "$newEvents new events (threshold: 50)" }
                        }
                    } catch {
                        Write-Verbose "Could not parse last update time: $_"
                    }
                }
            }
            return @{ should_trigger = $false; reason = "Event threshold not met" }
        }
        
        "time_threshold" {
            # Check time since last update
            $lastUpdate = Get-Content "kds-brain\knowledge-graph.yaml" -Raw -ErrorAction SilentlyContinue
            if ($lastUpdate -and $lastUpdate -match "last_updated:\s*[`"']?(.+?)[`"']?\s*$") {
                try {
                    $lastUpdateTime = [DateTime]::Parse($matches[1].Trim())
                    $hoursSince = ((Get-Date) - $lastUpdateTime).TotalHours
                    if ($hoursSince -ge 24) {
                        return @{ should_trigger = $true; reason = "$([math]::Round($hoursSince, 1)) hours since last update" }
                    }
                } catch {
                    Write-Verbose "Could not parse last update time: $_"
                }
            }
            return @{ should_trigger = $false; reason = "Time threshold not met" }
        }
        
        "manual" {
            return @{ should_trigger = $true; reason = "Manual trigger requested" }
        }
    }
}

# ============================================================================
# Main Logic
# ============================================================================
$check = Test-ShouldTriggerLearning -TriggerType $Trigger -IsWhatIf $WhatIf.IsPresent

if ($check.should_trigger) {
    Write-Host "🔔 Learning trigger activated: $($check.reason)" -ForegroundColor Green
    
    if (-not $WhatIf) {
        # Actually run the learning cycle
        Write-Host "⏳ Invoking learning cycle..." -ForegroundColor Cyan
        $cycleResult = & "$PSScriptRoot\run-learning-cycle.ps1"
        
        $result.learning_pipeline_invoked = $true
        $result.reason = $check.reason
        $result.cycle_result = $cycleResult
    } else {
        Write-Host "⚙️  WhatIf mode: Would invoke learning cycle" -ForegroundColor Yellow
        $result.learning_pipeline_invoked = $true
        $result.reason = $check.reason
    }
} else {
    Write-Verbose "Learning not triggered: $($check.reason)"
    $result.reason = $check.reason
}

return $result
