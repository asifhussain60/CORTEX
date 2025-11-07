# Similarity Analyzer Script
# Purpose: Calculate semantic similarity between two queries
# Part of: Right Brain Pattern Recognition (Week 3)

param(
    [Parameter(Mandatory=$true)]
    [string]$Query1,
    
    [Parameter(Mandatory=$true)]
    [string]$Query2,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Calculate word overlap similarity
function Get-WordOverlapSimilarity {
    param(
        [string]$Text1,
        [string]$Text2
    )
    
    $words1 = $Text1.ToLower() -split '\s+' | Where-Object { $_.Length -gt 2 }
    $words2 = $Text2.ToLower() -split '\s+' | Where-Object { $_.Length -gt 2 }
    
    if ($words1.Count -eq 0 -or $words2.Count -eq 0) {
        return 0.0
    }
    
    $commonWords = $words1 | Where-Object { $words2 -contains $_ }
    $similarity = $commonWords.Count / [math]::Max($words1.Count, $words2.Count)
    
    return $similarity
}

# Identify common components between queries
function Get-CommonComponents {
    param(
        [string]$Query1,
        [string]$Query2
    )
    
    $words1 = $Query1.ToLower() -split '\s+'
    $words2 = $Query2.ToLower() -split '\s+'
    
    $common = $words1 | Where-Object { $words2 -contains $_ }
    
    return $common
}

# In DryRun mode, simulate similarity analysis
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n🔬 Similarity Analysis (DRY RUN)" -ForegroundColor Cyan
        Write-Host "  Query 1: $Query1" -ForegroundColor Yellow
        Write-Host "  Query 2: $Query2" -ForegroundColor Yellow
    }
    
    return @{
        semantic_similarity = 0.85
        common_components = @("export", "add", "PDF")
        dry_run = $true
    }
}

# Real execution: Analyze similarity
try {
    Write-Host "`n🔬 Analyzing similarity..." -ForegroundColor Cyan
    Write-Host "  Query 1: '$Query1'" -ForegroundColor Yellow
    Write-Host "  Query 2: '$Query2'" -ForegroundColor Yellow
    
    $similarity = Get-WordOverlapSimilarity -Text1 $Query1 -Text2 $Query2
    $commonComponents = Get-CommonComponents -Query1 $Query1 -Query2 $Query2
    
    Write-Host "`n  📊 Results:" -ForegroundColor Cyan
    Write-Host "     Semantic Similarity: $([math]::Round($similarity * 100, 1))%" -ForegroundColor Green
    Write-Host "     Common Components: $($commonComponents.Count)" -ForegroundColor Green
    
    if ($commonComponents.Count -gt 0) {
        Write-Host "     Components: $($commonComponents -join ', ')" -ForegroundColor Gray
    }
    
    return @{
        semantic_similarity = $similarity
        common_components = $commonComponents
        query1 = $Query1
        query2 = $Query2
    }
    
} catch {
    Write-Host "  ❌ Similarity analysis error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        semantic_similarity = 0.0
        common_components = @()
        error = $_.Exception.Message
    }
}
