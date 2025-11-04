# Workflow Template Generator Script
# Purpose: Generate workflow template from pattern
# Part of: Right Brain Pattern Recognition (Week 3)

param(
    [Parameter(Mandatory=$true)]
    [string]$PatternId,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

# Load pattern by ID
function Get-Pattern {
    param([string]$PatternId)
    
    $patternFile = "$workspaceRoot\kds-brain\right-hemisphere\patterns\$PatternId.yaml"
    
    # Also check fixtures for testing
    if (-not (Test-Path $patternFile)) {
        $patternFile = "$workspaceRoot\tests\fixtures\patterns\sample-$PatternId.yaml"
    }
    
    if (-not (Test-Path $patternFile)) {
        throw "Pattern '$PatternId' not found"
    }
    
    $content = Get-Content $patternFile -Raw
    return $content
}

# In DryRun mode, simulate template generation
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n📋 Generating Workflow Template (DRY RUN)" -ForegroundColor Cyan
        Write-Host "  Pattern ID: $PatternId" -ForegroundColor Yellow
    }
    
    return @{
        phases = @(
            @{ phase_id = "phase_0"; phase_name = "Architectural Discovery" },
            @{ phase_id = "phase_1"; phase_name = "Test Infrastructure (RED)" },
            @{ phase_id = "phase_2"; phase_name = "Implementation (GREEN)" },
            @{ phase_id = "phase_3"; phase_name = "Refactoring (REFACTOR)" }
        )
        includes_tdd = $true
        includes_risk_assessment = $true
        includes_architectural_guidance = $true
        template_id = "$PatternId`_workflow"
        dry_run = $true
    }
}

# Real execution: Generate workflow template
try {
    Write-Host "`n📋 Generating workflow template for pattern: $PatternId" -ForegroundColor Cyan
    
    $patternContent = Get-Pattern -PatternId $PatternId
    
    # Parse pattern (simplified)
    $hasTDD = $patternContent -match "tdd_required:\s*true"
    $hasRiskAssessment = $patternContent -match "risk_factors:"
    $hasArchGuidance = $patternContent -match "architectural_guidance:"
    
    # Extract phases
    $phases = @()
    if ($patternContent -match "workflow_phases:") {
        # Count phase sections
        $phaseMatches = [regex]::Matches($patternContent, "phase_id:\s*(\w+)")
        foreach ($match in $phaseMatches) {
            $phaseId = $match.Groups[1].Value
            $phases += @{
                phase_id = $phaseId
                phase_name = "Phase $phaseId"
            }
        }
    }
    
    if ($phases.Count -eq 0) {
        # Default phases if none defined
        $phases = @(
            @{ phase_id = "phase_0"; phase_name = "Architectural Discovery" },
            @{ phase_id = "phase_1"; phase_name = "Test Infrastructure (RED)" },
            @{ phase_id = "phase_2"; phase_name = "Implementation (GREEN)" },
            @{ phase_id = "phase_3"; phase_name = "Refactoring (REFACTOR)" }
        )
    }
    
    Write-Host "  ✅ Template generated" -ForegroundColor Green
    Write-Host "     Phases: $($phases.Count)" -ForegroundColor Gray
    Write-Host "     TDD Required: $hasTDD" -ForegroundColor Gray
    Write-Host "     Risk Assessment: $hasRiskAssessment" -ForegroundColor Gray
    Write-Host "     Architectural Guidance: $hasArchGuidance" -ForegroundColor Gray
    
    return @{
        phases = $phases
        includes_tdd = $hasTDD
        includes_risk_assessment = $hasRiskAssessment
        includes_architectural_guidance = $hasArchGuidance
        template_id = "$PatternId`_workflow"
        pattern_id = $PatternId
    }
    
} catch {
    Write-Host "  ❌ Template generation error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        phases = @()
        includes_tdd = $false
        includes_risk_assessment = $false
        includes_architectural_guidance = $false
        error = $_.Exception.Message
    }
}
