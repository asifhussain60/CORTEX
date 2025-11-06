# Pattern Creator Script
# Purpose: Create new pattern from template or scratch
# Part of: Right Brain Pattern Recognition (Week 3)

param(
    [Parameter(Mandatory=$true)]
    [string]$PatternId,
    
    [Parameter(Mandatory=$true)]
    [string]$PatternName,
    
    [string]$Description = "",
    [string[]]$Keywords = @(),
    [double]$SimilarityThreshold = 0.70,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

# Validate pattern ID format
function Test-PatternIdFormat {
    param([string]$Id)
    
    return $Id -match '^[a-z_]+$'
}

# Create pattern YAML content
function New-PatternYaml {
    param(
        [string]$PatternId,
        [string]$PatternName,
        [string]$Description,
        [string[]]$Keywords,
        [double]$Threshold
    )
    
    $yaml = @"
pattern_id: $PatternId
pattern_name: "$PatternName"
description: "$Description"
similarity_threshold: $Threshold

keywords:
"@
    
    foreach ($keyword in $Keywords) {
        $yaml += "`n  - $keyword"
    }
    
    $yaml += @"

feature_components: []

workflow_phases: []

architectural_guidance: []

risk_factors: []

success_metrics:
  times_used: 0
  success_rate: 0.0
  average_duration_hours: 0.0

created_date: "$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')"
last_used: null
"@
    
    return $yaml
}

# In DryRun mode, simulate pattern creation
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n📝 Creating Pattern (DRY RUN)" -ForegroundColor Cyan
        Write-Host "  Pattern ID: $PatternId" -ForegroundColor Yellow
        Write-Host "  Pattern Name: $PatternName" -ForegroundColor Yellow
    }
    
    return @{
        pattern_created = $true
        pattern_id = $PatternId
        pattern_file = "cortex-brain/right-hemisphere/patterns/$PatternId.yaml"
        dry_run = $true
    }
}

# Real execution: Create pattern
try {
    Write-Host "`n📝 Creating new pattern..." -ForegroundColor Cyan
    
    # Validate pattern ID
    if (-not (Test-PatternIdFormat -Id $PatternId)) {
        throw "Pattern ID must be lowercase with underscores only (e.g., 'export_feature')"
    }
    
    # Check if pattern already exists
    $patternDir = "$workspaceRoot\cortex-brain\right-hemisphere\patterns"
    $patternFile = Join-Path $patternDir "$PatternId.yaml"
    
    if (Test-Path $patternFile) {
        throw "Pattern '$PatternId' already exists at $patternFile"
    }
    
    # Create pattern YAML
    $yamlContent = New-PatternYaml `
        -PatternId $PatternId `
        -PatternName $PatternName `
        -Description $Description `
        -Keywords $Keywords `
        -Threshold $SimilarityThreshold
    
    # Ensure directory exists
    if (-not (Test-Path $patternDir)) {
        New-Item -ItemType Directory -Path $patternDir -Force | Out-Null
    }
    
    # Write pattern file
    Set-Content -Path $patternFile -Value $yamlContent -Encoding UTF8
    
    Write-Host "  ✅ Pattern created: $PatternName" -ForegroundColor Green
    Write-Host "     File: $patternFile" -ForegroundColor Gray
    Write-Host "     ID: $PatternId" -ForegroundColor Gray
    
    return @{
        pattern_created = $true
        pattern_id = $PatternId
        pattern_name = $PatternName
        pattern_file = $patternFile
    }
    
} catch {
    Write-Host "  ❌ Pattern creation error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        pattern_created = $false
        error = $_.Exception.Message
    }
}
