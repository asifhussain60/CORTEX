# Monitor Learning Health
# Week 4 Phase 4: Continuous Learning Automation
# Tracks effectiveness of the learning system

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$result = @{
    effectiveness_score = 0.0
    learning_velocity = 0
    pattern_quality = 0.0
    recommendations = @()
    timestamp = (Get-Date).ToString("o")
}

if ($WhatIf) {
    Write-Host "⚙️  WhatIf mode: Would monitor learning health" -ForegroundColor Yellow
    $result.effectiveness_score = 0.85
    $result.learning_velocity = 12
    $result.pattern_quality = 0.78
    return $result
}

# ============================================================================
# Calculate Learning Effectiveness
# ============================================================================
function Get-LearningEffectiveness {
    $knowledgeGraph = Get-Content "cortex-brain\knowledge-graph.yaml" -Raw -ErrorAction SilentlyContinue
    
    if (-not $knowledgeGraph) {
        return 0.0
    }
    
    # Count patterns with high confidence
    $highConfidenceCount = ([regex]::Matches($knowledgeGraph, "confidence: 0\.[89]\d+")).Count
    $totalPatterns = ([regex]::Matches($knowledgeGraph, "confidence: 0\.\d+")).Count
    
    if ($totalPatterns -eq 0) {
        return 0.0
    }
    
    return [math]::Round($highConfidenceCount / $totalPatterns, 2)
}

# ============================================================================
# Calculate Learning Velocity
# ============================================================================
function Get-LearningVelocity {
    $eventsFile = "cortex-brain\events.jsonl"
    
    if (-not (Test-Path $eventsFile)) {
        return 0
    }
    
    $recentEvents = Get-Content $eventsFile |
        ForEach-Object { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue } |
        Where-Object { $_.timestamp -and (Get-Date $_.timestamp) -gt (Get-Date).AddDays(-7) }
    
    return $recentEvents.Count
}

# ============================================================================
# Calculate Pattern Quality
# ============================================================================
function Get-PatternQuality {
    $knowledgeGraph = Get-Content "cortex-brain\knowledge-graph.yaml" -Raw -ErrorAction SilentlyContinue
    
    if (-not $knowledgeGraph) {
        return 0.0
    }
    
    # Extract all confidence scores
    $confidenceScores = [regex]::Matches($knowledgeGraph, "confidence: (0\.\d+)") |
        ForEach-Object { [double]$_.Groups[1].Value }
    
    if ($confidenceScores.Count -eq 0) {
        return 0.0
    }
    
    $avgConfidence = ($confidenceScores | Measure-Object -Average).Average
    return [math]::Round($avgConfidence, 2)
}

# ============================================================================
# Generate Recommendations
# ============================================================================
function Get-HealthRecommendations {
    param(
        [double]$Effectiveness,
        [int]$Velocity,
        [double]$Quality
    )
    
    $recommendations = @()
    
    if ($Effectiveness -lt 0.6) {
        $recommendations += "Low effectiveness - Review pattern extraction logic"
    }
    
    if ($Velocity -lt 10) {
        $recommendations += "Low learning velocity - System needs more usage"
    }
    
    if ($Quality -lt 0.7) {
        $recommendations += "Low pattern quality - Review confidence calculation"
    }
    
    if ($Effectiveness -ge 0.8 -and $Velocity -ge 20 -and $Quality -ge 0.8) {
        $recommendations += "Excellent learning health - System performing optimally"
    }
    
    return $recommendations
}

# ============================================================================
# Main Monitoring
# ============================================================================
Write-Host "📊 Monitoring learning health..." -ForegroundColor Cyan

$result.effectiveness_score = Get-LearningEffectiveness
$result.learning_velocity = Get-LearningVelocity
$result.pattern_quality = Get-PatternQuality
$result.recommendations = Get-HealthRecommendations -Effectiveness $result.effectiveness_score `
    -Velocity $result.learning_velocity `
    -Quality $result.pattern_quality

Write-Host "`n📈 Learning Health Report:" -ForegroundColor Green
Write-Host "  Effectiveness: $($result.effectiveness_score * 100)%" -ForegroundColor White
Write-Host "  Velocity: $($result.learning_velocity) events/week" -ForegroundColor White
Write-Host "  Quality: $($result.pattern_quality * 100)%" -ForegroundColor White

if ($result.recommendations.Count -gt 0) {
    Write-Host "`n💡 Recommendations:" -ForegroundColor Yellow
    foreach ($rec in $result.recommendations) {
        Write-Host "  - $rec" -ForegroundColor White
    }
}

return $result
