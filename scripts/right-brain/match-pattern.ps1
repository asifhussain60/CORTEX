# Pattern Matcher Script
# Purpose: Find similar patterns from user query
# Part of: Right Brain Pattern Recognition (Week 3)

param(
    [Parameter(Mandatory=$true)]
    [string]$Query,
    
    [double]$MinimumSimilarity = 0.7,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

# Load pattern library
function Get-PatternLibrary {
    $patternDir = "$workspaceRoot\kds-brain\right-hemisphere\patterns"
    $patterns = @()
    
    if (Test-Path $patternDir) {
        Get-ChildItem -Path $patternDir -Filter "*.yaml" -File | ForEach-Object {
            $content = Get-Content $_.FullName -Raw
            $pattern = ConvertFrom-Yaml $content
            $patterns += $pattern
        }
    }
    
    # For testing: Load sample patterns from fixtures
    $fixtureDir = "$workspaceRoot\tests\fixtures\patterns"
    if (Test-Path $fixtureDir) {
        Get-ChildItem -Path $fixtureDir -Filter "*.yaml" -File | ForEach-Object {
            if ($_.Name -notlike "*template*") {
                $content = Get-Content $_.FullName -Raw
                $pattern = ConvertFrom-Yaml $content
                $patterns += $pattern
            }
        }
    }
    
    return $patterns
}

# Convert YAML to PowerShell object (simplified)
function ConvertFrom-Yaml {
    param([string]$Content)
    
    # Simplified YAML parser for our pattern structure
    $lines = $Content -split "`n"
    $obj = @{}
    $currentKey = $null
    $currentArray = @()
    $inArray = $false
    
    foreach ($line in $lines) {
        $line = $line.Trim()
        
        if ($line -match '^(\w+):\s*(.*)$') {
            $key = $matches[1]
            $value = $matches[2].Trim()
            
            if ($value -eq '') {
                $currentKey = $key
                $currentArray = @()
                $inArray = $true
            } else {
                $obj[$key] = $value.Trim('"', "'")
                $inArray = $false
            }
        }
        elseif ($line -match '^\s*-\s*(.+)$' -and $inArray) {
            $currentArray += $matches[1].Trim()
        }
        
        if ($inArray -and $currentKey -and $currentArray.Count -gt 0) {
            $obj[$currentKey] = $currentArray
        }
    }
    
    return $obj
}

# Calculate similarity between query and pattern
function Get-SimilarityScore {
    param(
        [string]$Query,
        [object]$Pattern
    )
    
    $queryWords = $Query.ToLower() -split '\s+'
    $keywords = @($Pattern.keywords)
    
    if (-not $keywords) {
        return 0.0
    }
    
    $matchCount = 0
    foreach ($word in $queryWords) {
        foreach ($keyword in $keywords) {
            if ($keyword.ToLower().Contains($word) -or $word.Contains($keyword.ToLower())) {
                $matchCount++
                break
            }
        }
    }
    
    $similarity = [math]::Min(1.0, $matchCount / [math]::Max(1, $queryWords.Count))
    return $similarity
}

# In DryRun mode, simulate pattern matching
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "`n🔍 Pattern Matching (DRY RUN)" -ForegroundColor Cyan
        Write-Host "  Query: $Query" -ForegroundColor Yellow
        Write-Host "  Minimum Similarity: $MinimumSimilarity" -ForegroundColor Yellow
    }
    
    return @{
        matches_found = $true
        pattern_id = "export_feature"
        pattern_name = "Export Feature Pattern"
        similarity_score = 0.87
        workflow_template = "export_feature_workflow"
        dry_run = $true
    }
}

# Real execution: Match patterns
try {
    Write-Host "`n🔍 Matching patterns for query: '$Query'" -ForegroundColor Cyan
    
    $patterns = Get-PatternLibrary
    
    if ($patterns.Count -eq 0) {
        Write-Host "  ⚠️  No patterns found in library" -ForegroundColor Yellow
        return @{
            matches_found = $false
            similarity_score = 0.0
            workflow_template = $null
        }
    }
    
    # Calculate similarity for each pattern
    $patternMatches = @()
    foreach ($pattern in $patterns) {
        $score = Get-SimilarityScore -Query $Query -Pattern $pattern
        
        if ($score -ge $MinimumSimilarity) {
            $patternMatches += @{
                pattern_id = $pattern.pattern_id
                pattern_name = $pattern.pattern_name
                similarity_score = $score
                workflow_template = "$($pattern.pattern_id)_workflow"
            }
        }
    }
    
    # Sort by similarity (highest first)
    $patternMatches = $patternMatches | Sort-Object -Property similarity_score -Descending
    
    if ($patternMatches.Count -gt 0) {
        $bestMatch = $patternMatches[0]
        
        Write-Host "  ✅ Found $($patternMatches.Count) matching pattern(s)" -ForegroundColor Green
        Write-Host "  📚 Best match: $($bestMatch.pattern_name)" -ForegroundColor Cyan
        Write-Host "     Similarity: $([math]::Round($bestMatch.similarity_score * 100, 1))%" -ForegroundColor Yellow
        
        return @{
            matches_found = $true
            pattern_id = $bestMatch.pattern_id
            pattern_name = $bestMatch.pattern_name
            similarity_score = $bestMatch.similarity_score
            workflow_template = $bestMatch.workflow_template
            all_matches = $patternMatches
        }
    } else {
        Write-Host "  ⚠️  No patterns matched (minimum similarity: $([math]::Round($MinimumSimilarity * 100, 1))%)" -ForegroundColor Yellow
        
        return @{
            matches_found = $false
            similarity_score = 0.0
            workflow_template = $null
        }
    }
    
} catch {
    Write-Host "  ❌ Pattern matching error: $($_.Exception.Message)" -ForegroundColor Red
    
    return @{
        matches_found = $false
        similarity_score = 0.0
        workflow_template = $null
        error = $_.Exception.Message
    }
}
