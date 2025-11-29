# Generate Proactive Warnings
# Week 4 Phase 5: Proactive Intelligence
# Creates user-friendly warnings from predictions

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [array]$Predictions,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$warnings = @()

if ($WhatIf) {
    Write-Host "⚙️  WhatIf mode: Would generate proactive warnings" -ForegroundColor Yellow
    return @(
        @{
            severity = "medium"
            message = "File is unstable - add comprehensive tests"
            confidence = 0.85
        }
    )
}

# ============================================================================
# Convert Predictions to Warnings
# ============================================================================
foreach ($prediction in $Predictions) {
    $warning = @{
        type = $prediction.type
        confidence = $prediction.confidence
        timestamp = (Get-Date).ToString("o")
    }
    
    switch ($prediction.type) {
        "file_hotspot" {
            $warning.severity = if ($prediction.churn_rate -gt 0.3) { "high" } 
                               elseif ($prediction.churn_rate -gt 0.2) { "medium" }
                               else { "low" }
            $warning.message = "⚠️ File '$($prediction.file)' is unstable ($(([math]::Round($prediction.churn_rate * 100)))% churn rate)"
            $warning.suggestion = "Add comprehensive tests before modifying"
            $warning.impact = "High risk of rework"
        }
        
        "complexity" {
            $warning.severity = "medium"
            $warning.message = "⚠️ Feature '$($prediction.feature)' involves multiple services"
            $warning.suggestion = "Use phased implementation approach"
            $warning.impact = "May take longer than estimated"
        }
        
        "historical" {
            $warning.severity = "low"
            $warning.message = "ℹ️ Similar features had issues in the past"
            $warning.suggestion = "Review historical patterns before starting"
            $warning.impact = "Can avoid common mistakes"
        }
        
        default {
            $warning.severity = "low"
            $warning.message = "ℹ️ $($prediction.message)"
            $warning.suggestion = "Proceed with caution"
        }
    }
    
    $warnings += $warning
}

# ============================================================================
# Display Warnings
# ============================================================================
if ($warnings.Count -gt 0) {
    Write-Host "`n⚠️  Proactive Warnings Generated:" -ForegroundColor Yellow
    
    foreach ($warning in $warnings) {
        $color = switch ($warning.severity) {
            "high" { "Red" }
            "medium" { "Yellow" }
            "low" { "Cyan" }
            default { "White" }
        }
        
        Write-Host "  [$($warning.severity.ToUpper())] $($warning.message)" -ForegroundColor $color
        Write-Host "    💡 Suggestion: $($warning.suggestion)" -ForegroundColor Gray
        Write-Host "    📊 Confidence: $([math]::Round($warning.confidence * 100))%" -ForegroundColor Gray
    }
}

return $warnings
