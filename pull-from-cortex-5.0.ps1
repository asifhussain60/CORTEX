#!/usr/bin/env pwsh
# Pull Tracker for CORTEX-5.5 Migration
# Version: 1.0.0
# Purpose: Track and validate pulls from CORTEX-5.0

param(
    [Parameter(Mandatory=$true)]
    [int]$Phase,
    
    [Parameter(Mandatory=$true)]
    [string[]]$Files,
    
    [Parameter(Mandatory=$true)]
    [string]$Justification,
    
    [Parameter(Mandatory=$false)]
    [string[]]$AlternativesConsidered,
    
    [Parameter(Mandatory=$false)]
    [string]$DecisionRationale,
    
    [Parameter(Mandatory=$false)]
    [string]$Category = "other"
)

$ErrorActionPreference = "Stop"

# Paths
$TRACKING_FILE = "cortex-brain/documents/planning/active/cortex5-enhancement-epic/tracking/pulls-from-cortex-5.0.json"
$SOURCE_BRANCH = "CORTEX-5.0"

# Validate files exist in CORTEX-5.0
Write-Host "🔍 Validating files in $SOURCE_BRANCH..." -ForegroundColor Cyan

foreach ($file in $Files) {
    $exists = git cat-file -e "$SOURCE_BRANCH`:$file" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ File not found in $SOURCE_BRANCH: $file" -ForegroundColor Red
        exit 1
    }
    
    # Check file age
    $lastModified = git log -1 --format="%ci" "$SOURCE_BRANCH`:$file" 2>$null
    $modDate = [DateTime]::Parse($lastModified)
    $daysSinceModified = ((Get-Date) - $modDate).Days
    
    if ($daysSinceModified -gt 90) {
        Write-Host "⚠️  File is $daysSinceModified days old (>90 days): $file" -ForegroundColor Yellow
        $response = Read-Host "Continue anyway? (yes/no)"
        if ($response -ne "yes") {
            Write-Host "❌ Pull cancelled by user" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "✅ All files validated" -ForegroundColor Green

# Load tracking JSON
$tracking = Get-Content $TRACKING_FILE -Raw | ConvertFrom-Json

# Check pull budget
if ($tracking.pull_budget.current_pull_count + $Files.Count -gt $tracking.pull_budget.max_pulls_allowed) {
    Write-Host "❌ Pull budget exceeded! ($($tracking.pull_budget.current_pull_count) + $($Files.Count) > $($tracking.pull_budget.max_pulls_allowed))" -ForegroundColor Red
    exit 1
}

# Warn if approaching threshold
if ($tracking.pull_budget.current_pull_count + $Files.Count -ge $tracking.pull_budget.alert_threshold) {
    Write-Host "⚠️  Approaching pull budget threshold ($($tracking.pull_budget.alert_threshold))" -ForegroundColor Yellow
}

# Pull files
Write-Host "`n📥 Pulling files from $SOURCE_BRANCH..." -ForegroundColor Cyan

foreach ($file in $Files) {
    git checkout $SOURCE_BRANCH -- $file
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (failed)" -ForegroundColor Red
        exit 1
    }
}

# Create pull record
$pullRecord = @{
    pull_id = $tracking.pulls.Count + 1
    phase = $Phase
    pull_date = (Get-Date -Format "yyyy-MM-dd")
    files_pulled = $Files
    file_count = $Files.Count
    justification = $Justification
    alternatives_considered = $AlternativesConsidered
    decision_rationale = $DecisionRationale
    category = $Category
    approved_by = "Phase Lead"
    dependencies_analyzed = $true
}

# Update tracking
$tracking.pulls += $pullRecord
$tracking.pull_budget.current_pull_count += $Files.Count
$tracking.pull_budget.remaining_pulls = $tracking.pull_budget.max_pulls_allowed - $tracking.pull_budget.current_pull_count
$tracking.tracking_metadata.last_updated = Get-Date -Format "yyyy-MM-dd"

# Update phase summary
$phaseSummary = $tracking.pull_summary_by_phase."phase_$Phase"
$phaseSummary.pulls += 1
$phaseSummary.files += $Files

# Update category
$categoryData = $tracking.pull_categories.$Category
$categoryData.pulls += 1
$categoryData.files += $Files

# Log alternatives
if ($AlternativesConsidered) {
    $tracking.alternatives_log += @{
        phase = $Phase
        alternatives = $AlternativesConsidered
        chosen = "Pull from CORTEX-5.0"
        rationale = $DecisionRationale
    }
}

# Save tracking
$tracking | ConvertTo-Json -Depth 10 | Set-Content $TRACKING_FILE

Write-Host "`n✅ Pull completed and tracked" -ForegroundColor Green
Write-Host "   Pull Budget: $($tracking.pull_budget.current_pull_count)/$($tracking.pull_budget.max_pulls_allowed) used" -ForegroundColor Cyan
Write-Host "   Phase $Phase: $($phaseSummary.pulls) pulls, $($phaseSummary.files.Count) files" -ForegroundColor Cyan

Write-Host "`n📝 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Validate pulled files work: pytest tests/" -ForegroundColor White
Write-Host "   2. Document in phase report: phases/phase-$Phase-*.md" -ForegroundColor White
Write-Host "   3. Commit changes: git add . && git commit -m 'chore(phase-$Phase): Pull dependencies from CORTEX-5.0'" -ForegroundColor White
