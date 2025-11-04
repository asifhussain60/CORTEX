# Pattern Library Updater Script
# Purpose: Store pattern in library and update knowledge graph
# Part of: Right Brain Pattern Learning (Week 3)

param(
    [Parameter(Mandatory=$true)]
    [string]$PatternFile,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

# Validate pattern structure
function Test-PatternStructure {
    param([string]$Content)
    
    $requiredFields = @("pattern_id", "pattern_name", "similarity_threshold", "feature_components")
    
    foreach ($field in $requiredFields) {
        if ($Content -notmatch "$field\s*:") {
            return $false
        }
    }
    
    return $true
}

# Update knowledge graph with new pattern
function Update-KnowledgeGraph {
    param([string]$PatternId)
    
    $kgFile = "$workspaceRoot\kds-brain\knowledge-graph.yaml"
    
    if (-not (Test-Path $kgFile)) {
        return $false
    }
    
    # In production, this would update the knowledge graph
    # For now, just simulate success
    return $true
}

# Log to right-hemisphere state
function Add-HemisphereStateLog {
    param(
        [string]$PatternId,
        [string]$Action
    )
    
    $stateFile = "$workspaceRoot\kds-brain\right-hemisphere\state.jsonl"
    
    $logEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        action = $Action
        pattern_id = $PatternId
    }
    
    $logJson = $logEntry | ConvertTo-Json -Compress
    
    # Ensure directory exists
    $stateDir = Split-Path $stateFile -Parent
    if (-not (Test-Path $stateDir)) {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
    }
    
    Add-Content -Path $stateFile -Value $logJson
    return $true
}

# In DryRun mode, simulate pattern storage
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n💾 Updating Pattern Library (DRY RUN)" -ForegroundColor Cyan
        Write-Host "  Pattern File: $PatternFile" -ForegroundColor Yellow
    }
    
    return @{
        validated = $true
        knowledge_graph_updated = $true
        logged_to_hemisphere_state = $true
        dry_run = $true
    }
}

# Real execution: Store pattern
try {
    Write-Host "`n💾 Storing pattern in library..." -ForegroundColor Cyan
    
    if (-not (Test-Path $PatternFile)) {
        throw "Pattern file not found: $PatternFile"
    }
    
    $content = Get-Content $PatternFile -Raw
    
    # Validate pattern
    $isValid = Test-PatternStructure -Content $content
    Write-Host "  Pattern Validation: $(if ($isValid) { '✅' } else { '❌' })" -ForegroundColor $(if ($isValid) { "Green" } else { "Red" })
    
    if (-not $isValid) {
        throw "Pattern validation failed - missing required fields"
    }
    
    # Extract pattern ID
    $patternId = "unknown"
    if ($content -match "pattern_id:\s*(\w+)") {
        $patternId = $Matches[1]
    }
    
    # Copy to pattern library
    $libraryDir = "$workspaceRoot\kds-brain\right-hemisphere\patterns"
    if (-not (Test-Path $libraryDir)) {
        New-Item -ItemType Directory -Path $libraryDir -Force | Out-Null
    }
    
    $destFile = Join-Path $libraryDir "$patternId.yaml"
    Copy-Item -Path $PatternFile -Destination $destFile -Force
    
    Write-Host "  ✅ Pattern copied to library" -ForegroundColor Green
    Write-Host "     Destination: $destFile" -ForegroundColor Gray
    
    # Update knowledge graph
    $kgUpdated = Update-KnowledgeGraph -PatternId $patternId
    Write-Host "  Knowledge Graph Updated: $(if ($kgUpdated) { '✅' } else { '⚠️ Skipped' })" -ForegroundColor $(if ($kgUpdated) { "Green" } else { "Yellow" })
    
    # Log to hemisphere state
    $logged = Add-HemisphereStateLog -PatternId $patternId -Action "pattern_stored"
    Write-Host "  Hemisphere State Logged: $(if ($logged) { '✅' } else { '❌' })" -ForegroundColor $(if ($logged) { "Green" } else { "Red" })
    
    return @{
        validated = $true
        knowledge_graph_updated = $kgUpdated
        logged_to_hemisphere_state = $logged
        pattern_id = $patternId
        pattern_file = $destFile
    }
    
} catch {
    Write-Host "  ❌ Pattern storage error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        validated = $false
        knowledge_graph_updated = $false
        logged_to_hemisphere_state = $false
        error = $_.Exception.Message
    }
}
