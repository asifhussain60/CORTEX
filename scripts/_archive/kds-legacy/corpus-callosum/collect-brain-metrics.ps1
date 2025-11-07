# Collect Brain Metrics
# Week 4 Phase 6: Performance Monitoring
# Gathers performance metrics from all brain components

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$metrics = @{
    routing_accuracy = 0.0
    plan_creation_time = 0
    tdd_cycle_time = 0
    learning_effectiveness = 0.0
    coordination_latency = 0
    timestamp = (Get-Date).ToString("o")
}

if ($WhatIf) {
    Write-Host "⚙️  WhatIf mode: Would collect brain metrics" -ForegroundColor Yellow
    $metrics.routing_accuracy = 0.94
    $metrics.plan_creation_time = 120  # seconds
    $metrics.tdd_cycle_time = 45  # seconds
    $metrics.learning_effectiveness = 0.87
    $metrics.coordination_latency = 3  # seconds
    return $metrics
}

# ============================================================================
# Routing Accuracy
# ============================================================================
function Get-RoutingAccuracy {
    $eventsFile = "cortex-brain\events.jsonl"
    
    if (-not (Test-Path $eventsFile)) {
        return 0.0
    }
    
    $routingEvents = Get-Content $eventsFile |
        ForEach-Object { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue } |
        Where-Object { $_.type -eq "intent_detected" -and $_.timestamp -and (Get-Date $_.timestamp) -gt (Get-Date).AddDays(-7) }
    
    if ($routingEvents.Count -eq 0) {
        return 0.0
    }
    
    # Count high-confidence routings
    $highConfidence = ($routingEvents | Where-Object { $_.confidence -ge 0.8 }).Count
    
    return [math]::Round($highConfidence / $routingEvents.Count, 2)
}

# ============================================================================
# Plan Creation Time
# ============================================================================
function Get-AveragePlanTime {
    $planningState = "cortex-brain\right-hemisphere\planning-state.jsonl"
    
    if (-not (Test-Path $planningState)) {
        return 0
    }
    
    $planEvents = Get-Content $planningState |
        ForEach-Object { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue } |
        Where-Object { $_.phase_duration -and $_.timestamp -and (Get-Date $_.timestamp) -gt (Get-Date).AddDays(-7) }
    
    if ($planEvents.Count -eq 0) {
        return 0
    }
    
    $avgSeconds = ($planEvents | Measure-Object -Property phase_duration -Average).Average
    return [math]::Round($avgSeconds)
}

# ============================================================================
# TDD Cycle Time
# ============================================================================
function Get-AverageTDDCycleTime {
    $executionState = "cortex-brain\left-hemisphere\execution-state.jsonl"
    
    if (-not (Test-Path $executionState)) {
        return 0
    }
    
    $tddEvents = Get-Content $executionState |
        ForEach-Object { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue } |
        Where-Object { $_.tdd_cycle_time -and $_.timestamp -and (Get-Date $_.timestamp) -gt (Get-Date).AddDays(-7) }
    
    if ($tddEvents.Count -eq 0) {
        return 0
    }
    
    $avgSeconds = ($tddEvents | Measure-Object -Property tdd_cycle_time -Average).Average
    return [math]::Round($avgSeconds)
}

# ============================================================================
# Learning Effectiveness
# ============================================================================
function Get-LearningEffectiveness {
    $knowledgeGraph = Get-Content "cortex-brain\knowledge-graph.yaml" -Raw -ErrorAction SilentlyContinue
    
    if (-not $knowledgeGraph) {
        return 0.0
    }
    
    # Count high-confidence patterns
    $highConfidence = ([regex]::Matches($knowledgeGraph, "confidence: 0\.[89]\d+")).Count
    $totalPatterns = ([regex]::Matches($knowledgeGraph, "confidence: 0\.\d+")).Count
    
    if ($totalPatterns -eq 0) {
        return 0.0
    }
    
    return [math]::Round($highConfidence / $totalPatterns, 2)
}

# ============================================================================
# Coordination Latency
# ============================================================================
function Get-CoordinationLatency {
    $coordinationQueue = "cortex-brain\corpus-callosum\coordination-queue.jsonl"
    
    if (-not (Test-Path $coordinationQueue)) {
        return 0
    }
    
    $messages = Get-Content $coordinationQueue |
        ForEach-Object { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue } |
        Where-Object { $_.sent_at -and $_.received_at }
    
    if ($messages.Count -eq 0) {
        return 0
    }
    
    $latencies = $messages | ForEach-Object {
        $sent = Get-Date $_.sent_at
        $received = Get-Date $_.received_at
        ($received - $sent).TotalSeconds
    }
    
    $avgLatency = ($latencies | Measure-Object -Average).Average
    return [math]::Round($avgLatency)
}

# ============================================================================
# Collect All Metrics
# ============================================================================
Write-Host "📊 Collecting brain performance metrics..." -ForegroundColor Cyan

$metrics.routing_accuracy = Get-RoutingAccuracy
$metrics.plan_creation_time = Get-AveragePlanTime
$metrics.tdd_cycle_time = Get-AverageTDDCycleTime
$metrics.learning_effectiveness = Get-LearningEffectiveness
$metrics.coordination_latency = Get-CoordinationLatency

Write-Host "`n📈 Brain Performance Metrics:" -ForegroundColor Green
Write-Host "  Routing Accuracy: $($metrics.routing_accuracy * 100)%" -ForegroundColor White
Write-Host "  Avg Plan Time: $($metrics.plan_creation_time)s" -ForegroundColor White
Write-Host "  Avg TDD Cycle: $($metrics.tdd_cycle_time)s" -ForegroundColor White
Write-Host "  Learning Effectiveness: $($metrics.learning_effectiveness * 100)%" -ForegroundColor White
Write-Host "  Coordination Latency: $($metrics.coordination_latency)s" -ForegroundColor White

# Save metrics to history
$historyFile = "cortex-brain\corpus-callosum\efficiency-history.jsonl"
$historyDir = Split-Path $historyFile -Parent
if (-not (Test-Path $historyDir)) {
    New-Item -ItemType Directory -Path $historyDir -Force | Out-Null
}

$metrics | ConvertTo-Json -Compress | Add-Content $historyFile

return $metrics
