# Analyze Brain Efficiency
# Week 4 Phase 6: Performance Monitoring
# Calculates overall brain efficiency score

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [hashtable]$Metrics,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$result = @{
    score = 0.0
    components = @{}
    grade = ""
    recommendations = @()
    timestamp = (Get-Date).ToString("o")
}

if ($WhatIf) {
    Write-Host "⚙️  WhatIf mode: Would analyze brain efficiency" -ForegroundColor Yellow
    $result.score = 0.82
    $result.grade = "B+"
    return $result
}

# ============================================================================
# Load Metrics
# ============================================================================
if (-not $Metrics) {
    Write-Host "📊 Collecting current metrics..." -ForegroundColor Cyan
    $Metrics = & "$PSScriptRoot\collect-brain-metrics.ps1"
}

# ============================================================================
# Calculate Component Scores
# ============================================================================

# Routing Efficiency (0-1)
$routingScore = $Metrics.routing_accuracy
$result.components.routing = $routingScore

# Planning Efficiency (faster is better, normalize to 0-1)
$planScore = if ($Metrics.plan_creation_time -eq 0) { 0.5 }
             elseif ($Metrics.plan_creation_time -le 60) { 1.0 }
             elseif ($Metrics.plan_creation_time -le 180) { 0.8 }
             elseif ($Metrics.plan_creation_time -le 300) { 0.6 }
             else { 0.4 }
$result.components.planning = $planScore

# TDD Efficiency (faster is better, normalize to 0-1)
$tddScore = if ($Metrics.tdd_cycle_time -eq 0) { 0.5 }
            elseif ($Metrics.tdd_cycle_time -le 30) { 1.0 }
            elseif ($Metrics.tdd_cycle_time -le 60) { 0.9 }
            elseif ($Metrics.tdd_cycle_time -le 120) { 0.7 }
            else { 0.5 }
$result.components.tdd = $tddScore

# Learning Efficiency (0-1)
$learningScore = $Metrics.learning_effectiveness
$result.components.learning = $learningScore

# Coordination Efficiency (lower latency is better, normalize to 0-1)
$coordScore = if ($Metrics.coordination_latency -eq 0) { 0.8 }
              elseif ($Metrics.coordination_latency -le 5) { 1.0 }
              elseif ($Metrics.coordination_latency -le 10) { 0.8 }
              elseif ($Metrics.coordination_latency -le 20) { 0.6 }
              else { 0.4 }
$result.components.coordination = $coordScore

# ============================================================================
# Calculate Overall Score
# ============================================================================
$weights = @{
    routing = 0.25
    planning = 0.20
    tdd = 0.20
    learning = 0.25
    coordination = 0.10
}

$totalScore = 0.0
foreach ($component in $result.components.Keys) {
    $totalScore += $result.components[$component] * $weights[$component]
}

$result.score = [math]::Round($totalScore, 2)

# ============================================================================
# Assign Grade
# ============================================================================
$result.grade = if ($result.score -ge 0.95) { "A+" }
                elseif ($result.score -ge 0.90) { "A" }
                elseif ($result.score -ge 0.85) { "A-" }
                elseif ($result.score -ge 0.80) { "B+" }
                elseif ($result.score -ge 0.75) { "B" }
                elseif ($result.score -ge 0.70) { "B-" }
                elseif ($result.score -ge 0.65) { "C+" }
                elseif ($result.score -ge 0.60) { "C" }
                else { "D" }

# ============================================================================
# Generate Recommendations
# ============================================================================
if ($routingScore -lt 0.8) {
    $result.recommendations += "Improve routing accuracy - Review intent patterns"
}

if ($planScore -lt 0.7) {
    $result.recommendations += "Reduce planning time - Optimize pattern matching"
}

if ($tddScore -lt 0.7) {
    $result.recommendations += "Reduce TDD cycle time - Streamline test execution"
}

if ($learningScore -lt 0.7) {
    $result.recommendations += "Improve learning - Review pattern extraction quality"
}

if ($coordScore -lt 0.7) {
    $result.recommendations += "Reduce coordination latency - Optimize message queue"
}

if ($result.score -ge 0.85) {
    $result.recommendations += "Excellent performance - Brain operating optimally!"
}

# ============================================================================
# Display Results
# ============================================================================
Write-Host "`n📊 Brain Efficiency Analysis:" -ForegroundColor Cyan
Write-Host ("=" * 60)

$gradeColor = if ($result.score -ge 0.8) { "Green" }
              elseif ($result.score -ge 0.6) { "Yellow" }
              else { "Red" }

Write-Host "`n  Overall Score: $($result.score * 100)% (Grade: $($result.grade))" -ForegroundColor $gradeColor

Write-Host "`n  Component Scores:" -ForegroundColor White
foreach ($component in $result.components.Keys | Sort-Object) {
    $score = $result.components[$component]
    $bar = "█" * [math]::Round($score * 20)
    $emptyBar = "░" * (20 - [math]::Round($score * 20))
    Write-Host "    $($component.PadRight(15)): [$bar$emptyBar] $([math]::Round($score * 100))%" -ForegroundColor Cyan
}

if ($result.recommendations.Count -gt 0) {
    Write-Host "`n  💡 Recommendations:" -ForegroundColor Yellow
    foreach ($rec in $result.recommendations) {
        Write-Host "    - $rec" -ForegroundColor White
    }
}

Write-Host ""

return $result
