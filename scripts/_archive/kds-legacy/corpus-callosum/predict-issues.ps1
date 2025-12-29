# Predict Issues
# Week 4 Phase 5: Proactive Intelligence
# Predicts potential problems before they occur

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$Request,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$predictions = @()

if ($WhatIf) {
    Write-Host "⚙️  WhatIf mode: Would predict issues for request" -ForegroundColor Yellow
    return @(
        @{
            type = "file_hotspot"
            confidence = 0.72
            message = "File modification may require extra testing"
        }
    )
}

# ============================================================================
# Load Context
# ============================================================================
$developmentContext = Get-Content "cortex-brain\development-context.yaml" -Raw -ErrorAction SilentlyContinue | ConvertFrom-Yaml -ErrorAction SilentlyContinue
$knowledgeGraph = Get-Content "cortex-brain\knowledge-graph.yaml" -Raw -ErrorAction SilentlyContinue

# ============================================================================
# Extract Entities from Request
# ============================================================================
function Extract-RequestEntities {
    param([string]$Text)
    
    $entities = @{
        files = @()
        features = @()
        components = @()
    }
    
    # File patterns
    if ($Text -match "(\w+\.(cs|razor|css|js|ts))") {
        $entities.files += $matches[1]
    }
    
    # Feature patterns
    if ($Text -match "(add|create|implement) (.+?) (to|for|in)") {
        $entities.features += $matches[2]
    }
    
    return $entities
}

# ============================================================================
# Predict Based on Hotspots
# ============================================================================
function Predict-HotspotIssues {
    param([array]$Files)
    
    $issues = @()
    
    foreach ($file in $Files) {
        if ($developmentContext -and $developmentContext.code_changes.hotspots) {
            $hotspot = $developmentContext.code_changes.hotspots | Where-Object { $_.file -like "*$file*" } | Select-Object -First 1
            
            if ($hotspot -and $hotspot.churn_rate -gt 0.2) {
                $issues += @{
                    type = "file_hotspot"
                    file = $file
                    churn_rate = $hotspot.churn_rate
                    confidence = [math]::Min(0.5 + ($hotspot.churn_rate * 2), 0.95)
                    message = "File '$file' is a hotspot ($(([math]::Round($hotspot.churn_rate * 100)))% churn) - extra testing recommended"
                }
            }
        }
    }
    
    return $issues
}

# ============================================================================
# Predict Based on Complexity
# ============================================================================
function Predict-ComplexityIssues {
    param([array]$Features)
    
    $issues = @()
    
    foreach ($feature in $Features) {
        $lowerFeature = $feature.ToLower()
        
        # Multi-service features are complex
        if ($lowerFeature -match "(multi|export|import|integration)") {
            $issues += @{
                type = "complexity"
                feature = $feature
                confidence = 0.72
                message = "Feature involves multiple services - consider phased approach"
            }
        }
        
        # PDF/Email features often complex
        if ($lowerFeature -match "(pdf|email|report|export)") {
            $issues += @{
                type = "complexity"
                feature = $feature
                confidence = 0.68
                message = "External service integration - plan for error handling"
            }
        }
    }
    
    return $issues
}

# ============================================================================
# Predict Based on Historical Failures
# ============================================================================
function Predict-HistoricalIssues {
    param([string]$RequestText)
    
    $issues = @()
    
    # Check knowledge graph for similar failed requests
    if ($knowledgeGraph -and $knowledgeGraph -match "common_mistakes:") {
        # Parse common mistakes section
        $mistakesSection = $knowledgeGraph -split "common_mistakes:" | Select-Object -Last 1
        
        if ($mistakesSection -match "validation_insights:") {
            $mistakesSection = $mistakesSection -split "validation_insights:" | Select-Object -First 1
        }
        
        # Check for relevant mistakes
        if ($RequestText -match "button" -and $mistakesSection -match "button") {
            $issues += @{
                type = "historical"
                confidence = 0.65
                message = "Similar button features had issues in past - review button patterns"
            }
        }
    }
    
    return $issues
}

# ============================================================================
# Main Prediction
# ============================================================================
Write-Host "🔮 Predicting issues for: $Request" -ForegroundColor Cyan

$entities = Extract-RequestEntities -Text $Request

$predictions += Predict-HotspotIssues -Files $entities.files
$predictions += Predict-ComplexityIssues -Features $entities.features
$predictions += Predict-HistoricalIssues -RequestText $Request

if ($predictions.Count -gt 0) {
    Write-Host "⚠️  Predicted $($predictions.Count) potential issue(s):" -ForegroundColor Yellow
    foreach ($pred in $predictions) {
        Write-Host "  - [$($pred.type)] $($pred.message) (confidence: $([math]::Round($pred.confidence * 100))%)" -ForegroundColor White
    }
} else {
    Write-Host "✅ No significant issues predicted" -ForegroundColor Green
}

return $predictions
