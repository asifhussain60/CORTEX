# Run Learning Cycle
# Week 4 Phase 4: Continuous Learning Automation
# Executes the complete learning pipeline

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

$result = @{
    patterns_extracted = 0
    patterns_merged = 0
    knowledge_graph_updated = $false
    duration_ms = 0
    timestamp = (Get-Date).ToString("o")
}

if ($WhatIf) {
    Write-Host "⚙️  WhatIf mode: Would run complete learning cycle" -ForegroundColor Yellow
    $result.patterns_extracted = 15
    $result.patterns_merged = 3
    $result.knowledge_graph_updated = $true
    return $result
}

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "🧠 Starting learning cycle..." -ForegroundColor Cyan

# ============================================================================
# Step 1: Extract patterns from events
# ============================================================================
Write-Host "  📊 Step 1: Extracting patterns from events..." -ForegroundColor White
$patterns = & "$PSScriptRoot\extract-patterns-from-events.ps1"
$result.patterns_extracted = $patterns.Count
Write-Host "    ✅ Extracted $($patterns.Count) patterns" -ForegroundColor Green

# ============================================================================
# Step 2: Calculate confidence scores
# ============================================================================
Write-Host "  🎯 Step 2: Calculating confidence scores..." -ForegroundColor White
$patternsWithConfidence = @()
foreach ($pattern in $patterns) {
    $withConfidence = & "$PSScriptRoot\calculate-pattern-confidence.ps1" -Pattern $pattern
    $patternsWithConfidence += $withConfidence
}
Write-Host "    ✅ Assigned confidence scores" -ForegroundColor Green

# ============================================================================
# Step 3: Merge similar patterns
# ============================================================================
Write-Host "  🔀 Step 3: Merging similar patterns..." -ForegroundColor White
$mergedPatterns = & "$PSScriptRoot\merge-patterns.ps1" -Patterns $patternsWithConfidence
$result.patterns_merged = $patternsWithConfidence.Count - $mergedPatterns.Count
Write-Host "    ✅ Merged $($result.patterns_merged) duplicate patterns" -ForegroundColor Green

# ============================================================================
# Step 4: Update knowledge graph
# ============================================================================
Write-Host "  💾 Step 4: Updating knowledge graph..." -ForegroundColor White
& "$PSScriptRoot\update-knowledge-graph-learning.ps1" -Patterns $mergedPatterns
$result.knowledge_graph_updated = $true
Write-Host "    ✅ Knowledge graph updated" -ForegroundColor Green

$stopwatch.Stop()
$result.duration_ms = $stopwatch.ElapsedMilliseconds

Write-Host "`n✅ Learning cycle complete in $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Green
Write-Host "  - Patterns extracted: $($result.patterns_extracted)" -ForegroundColor White
Write-Host "  - Patterns merged: $($result.patterns_merged)" -ForegroundColor White
Write-Host "  - Knowledge graph: Updated" -ForegroundColor White

return $result
