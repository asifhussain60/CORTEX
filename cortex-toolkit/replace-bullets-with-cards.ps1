<#
.SYNOPSIS
    Intelligently replaces bullet lists with glassmorphism cards based on content analysis
.DESCRIPTION
    Converts <ul> lists to card layouts per Principle 13 (v4.2.3) using content-driven decision matrix.
    Preserves bullets for: short items (<50 chars), semantic lists, contained contexts, 3-6 items.
    Converts to cards for: long descriptions (>100 chars), visual prominence, rich content.
.PARAMETER DryRun
    Preview changes without modifying files
.PARAMETER AnalyzeContent
    Enable intelligent content analysis (default: true)
.PARAMETER Force
    Bypass content analysis and convert all lists (legacy behavior)
#>

param(
    [switch]$DryRun = $false,
    [switch]$AnalyzeContent = $true,
    [switch]$Force = $false
)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$htmlFiles = Get-ChildItem -Path $DocsRoot -Filter "*.html" -Recurse -File |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

$filesUpdated = 0
$listsReplaced = 0
$listsPreserved = 0

# Preservation class patterns (NEVER convert)
$preservationClasses = @(
    'persona-benefits',
    'feature-list',
    'navigation-list',
    'step-list',
    'benefits-container',
    'quick-reference',
    'nav-list',
    'menu-list'
)

# Conversion class patterns (ALWAYS convert)
$conversionClasses = @(
    'feature-showcase',
    'integration-grid',
    'capability-highlights',
    'team-members',
    'case-studies',
    'product-showcase'
)

function Test-ShouldConvertToCards {
    param([string]$listContent, [string]$parentContext)
    
    # Force mode: convert everything (legacy behavior)
    if ($Force) { return $true }
    
    # Check preservation classes (NEVER convert)
    foreach ($class in $preservationClasses) {
        if ($listContent -match "class=[`"'][^`"']*$class[^`"']*[`"']" -or 
            $parentContext -match "class=[`"'][^`"']*$class[^`"']*[`"']") {
            return $false
        }
    }
    
    # Check conversion classes (ALWAYS convert)
    foreach ($class in $conversionClasses) {
        if ($listContent -match "class=[`"'][^`"']*$class[^`"']*[`"']" -or 
            $parentContext -match "class=[`"'][^`"']*$class[^`"']*[`"']") {
            return $true
        }
    }
    
    # Content analysis if AnalyzeContent enabled
    if ($AnalyzeContent) {
        # Extract list items
        $items = [regex]::Matches($listContent, '<li[^>]*>([\s\S]*?)<\/li>')
        if ($items.Count -eq 0) { return $false }
        
        # Calculate average character length (excluding HTML tags)
        $totalChars = 0
        foreach ($item in $items) {
            $textContent = $item.Groups[1].Value -replace '<[^>]+>', ''
            $totalChars += $textContent.Trim().Length
        }
        $avgLength = $totalChars / $items.Count
        
        # Decision tree based on content characteristics
        # SHORT ITEMS (3-6 items, <50 chars avg) → BULLETS
        if ($items.Count -ge 3 -and $items.Count -le 6 -and $avgLength -lt 50) {
            return $false
        }
        
        # LONG DESCRIPTIONS (>100 chars avg) → CARDS
        if ($avgLength -gt 100) {
            return $true
        }
        
        # MEDIUM LENGTH: Check semantic context
        # If inside styled container (persona-tile, glass-panel), prefer bullets
        if ($parentContext -match 'persona-tile|glass-panel|benefits-section') {
            return $false
        }
        
        # DEFAULT: 7+ items or standalone lists → CARDS
        if ($items.Count -ge 7) {
            return $true
        }
    }
    
    # Default: preserve bullets (conservative approach)
    return $false
}

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    $originalContent = $content
    
    # Pattern: Find <ul> lists with parent context (200 chars before)
    $featurePattern = '(?s)(.{0,200})<ul([^>]*)>([\s\S]*?)<\/ul>'
    $matches = [regex]::Matches($content, $featurePattern)
    
    foreach ($match in $matches) {
        $parentContext = $match.Groups[1].Value
        $ulAttributes = $match.Groups[2].Value
        $listContent = $match.Groups[3].Value
        $fullMatch = $match.Value
        
        # Only convert lists with multiple items (3+)
        $itemCount = ([regex]::Matches($listContent, '<li')).Count
        if ($itemCount -lt 3) { continue }
        
        # Skip navigation links
        if ($listContent -match '<li[^>]*>\s*<a[^>]*>.*?<\/a>\s*<\/li>' -and 
            $parentContext -match 'nav|menu') { 
            continue 
        }
        
        # Intelligent decision: should we convert?
        $shouldConvert = Test-ShouldConvertToCards -listContent "<ul$ulAttributes>$listContent</ul>" -parentContext $parentContext
        
        if ($shouldConvert) {
            # Extract list items and convert to cards
            $items = [regex]::Matches($listContent, '<li[^>]*>([\s\S]*?)<\/li>')
            $cardHtml = '<div class="capability-tiles">'
            
            foreach ($item in $items) {
                $itemContent = $item.Groups[1].Value.Trim()
                $cardHtml += "`n    <div class=`"glass-card`">`n        <div class=`"card-body`">$itemContent</div>`n    </div>"
            }
            
            $cardHtml += "`n</div>"
            
            # Replace the <ul>...</ul> portion only (preserve parent context)
            $ulPattern = [regex]::Escape("<ul$ulAttributes>$listContent</ul>")
            $content = $content -replace $ulPattern, $cardHtml
            $listsReplaced++
        } else {
            $listsPreserved++
        }
    }
    
    if ($content -ne $originalContent -and -not $DryRun) {
        $content | Out-File $file.FullName -Encoding UTF8 -NoNewline
        $filesUpdated++
    }
}

if ($DryRun) {
    Write-Host "`n🔍 DRY RUN ANALYSIS" -ForegroundColor Cyan
    Write-Host "Would convert: $listsReplaced lists → cards" -ForegroundColor Yellow
    Write-Host "Would preserve: $listsPreserved lists → bullets" -ForegroundColor Green
    Write-Host "Files affected: ~$filesUpdated" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ CONVERSION COMPLETE" -ForegroundColor Green
    Write-Host "Converted: $listsReplaced lists → cards" -ForegroundColor Green
    Write-Host "Preserved: $listsPreserved lists → bullets" -ForegroundColor Cyan
    Write-Host "Files updated: $filesUpdated" -ForegroundColor Green
    
    if (-not $AnalyzeContent -and -not $Force) {
        Write-Host "`n💡 TIP: Run with -AnalyzeContent for intelligent detection" -ForegroundColor Yellow
    }
}

# Show decision summary
Write-Host "`n📊 DECISION CRITERIA APPLIED:" -ForegroundColor Cyan
Write-Host "  • Preservation classes: $($preservationClasses -join ', ')"
Write-Host "  • Conversion classes: $($conversionClasses -join ', ')"
if ($AnalyzeContent) {
    Write-Host "  • Content analysis: ENABLED (3-6 items <50 chars → bullets)"
    Write-Host "  • Long descriptions: >100 chars → cards"
} else {
    Write-Host "  • Content analysis: DISABLED"
}
if ($Force) {
    Write-Host "  • Force mode: ACTIVE (converted all lists)" -ForegroundColor Yellow
}
