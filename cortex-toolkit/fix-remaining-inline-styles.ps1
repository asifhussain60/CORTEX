<#
.SYNOPSIS
    Fixes remaining 145 inline styles that couldn't be auto-converted
.DESCRIPTION
    Handles complex inline styles with manual CSS class generation
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$cssFile = Join-Path $DocsRoot "assets\css\generated-classes.css"
$htmlFiles = Get-ChildItem -Path $DocsRoot -Filter "*.html" -Recurse -File |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

$inlineStyles = @{}
$filesUpdated = 0

# Collect remaining inline styles
foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    $matches = [regex]::Matches($content, 'style="([^"]+)"')
    
    foreach ($match in $matches) {
        $style = $match.Groups[1].Value
        if (-not $inlineStyles.ContainsKey($style)) {
            $inlineStyles[$style] = @()
        }
        $inlineStyles[$style] += $file.FullName
    }
}

Write-Host "Found $($inlineStyles.Count) unique inline styles" -ForegroundColor Cyan

if ($inlineStyles.Count -eq 0) {
    Write-Host "✅ No inline styles to fix!" -ForegroundColor Green
    exit 0
}

# Generate CSS classes for remaining styles
$cssContent = "`n/* Auto-generated fixes for remaining inline styles - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') */`n"
$classCounter = 183 # Continue from previous generation

$replacements = @{}

foreach ($style in $inlineStyles.Keys | Sort-Object { $inlineStyles[$_].Count } -Descending) {
    $className = "inline-fix-$classCounter"
    $cssContent += "`n.$className {`n"
    
    # Parse style into individual properties
    $properties = $style -split ';' | Where-Object { $_ -match '\S' }
    foreach ($prop in $properties) {
        $prop = $prop.Trim()
        if ($prop -match '^\s*$') { continue }
        if ($prop -notmatch ':') { continue }
        $cssContent += "    $prop"
        if (-not $prop.EndsWith(';')) { $cssContent += ';' }
        $cssContent += "`n"
    }
    
    $cssContent += "}`n"
    $replacements[$style] = $className
    $classCounter++
}

if (-not $DryRun) {
    # Append to existing CSS file
    Add-Content -Path $cssFile -Value $cssContent -Encoding UTF8
    
    # Replace inline styles with classes
    foreach ($file in $htmlFiles) {
        $content = Get-Content $file.FullName -Raw
        $originalContent = $content
        
        foreach ($style in $replacements.Keys) {
            $className = $replacements[$style]
            $pattern = [regex]::Escape("style=`"$style`"")
            $content = $content -replace $pattern, "class=`"$className`""
        }
        
        if ($content -ne $originalContent) {
            $content | Out-File $file.FullName -Encoding UTF8 -NoNewline
            $filesUpdated++
        }
    }
    
    Write-Host "✅ Generated $($replacements.Count) new CSS classes" -ForegroundColor Green
    Write-Host "✅ Updated $filesUpdated HTML files" -ForegroundColor Green
} else {
    Write-Host "Would generate $($replacements.Count) CSS classes" -ForegroundColor Yellow
    Write-Host "Would update HTML files" -ForegroundColor Yellow
}
