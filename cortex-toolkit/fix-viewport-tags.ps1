<#
.SYNOPSIS
    Adds missing viewport meta tags to HTML files
.DESCRIPTION
    Scans HTML files for missing viewport meta tags and adds them to the <head> section
.EXAMPLE
    .\fix-viewport-tags.ps1
.NOTES
    Version: 1.0.0
    Author: Asif Hussain
    Created: January 3, 2026
#>

param(
    [switch]$DryRun = $false
)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$ReportPath = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports\viewport-fixes-$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

Write-Host "📱 Viewport Meta Tag Fixer" -ForegroundColor Cyan
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'EXECUTE' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })

# Get all HTML files
$htmlFiles = Get-ChildItem -Path $DocsRoot -Filter "*.html" -Recurse -File |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

$missingViewport = @()
$filesFixed = 0

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Check if viewport meta tag exists
    if ($content -notmatch '<meta\s+name="viewport"') {
        $missingViewport += $file.FullName
        
        if (-not $DryRun) {
            # Find the <head> tag and add viewport after charset or at beginning
            if ($content -match '(<head[^>]*>)(\s*)(<meta\s+charset="[^"]+">)?') {
                $viewportTag = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                
                if ($matches[3]) {
                    # Add after charset
                    $replacement = "$($matches[1])$($matches[2])$($matches[3])`n    $viewportTag"
                    $content = $content -replace [regex]::Escape($matches[0]), $replacement
                } else {
                    # Add right after <head>
                    $replacement = "$($matches[1])$($matches[2])`n    $viewportTag"
                    $content = $content -replace [regex]::Escape($matches[0]), $replacement
                }
                
                $content | Out-File $file.FullName -Encoding UTF8 -NoNewline
                $filesFixed++
            }
        }
    }
}

Write-Host "🔍 Found $($missingViewport.Count) files missing viewport meta tags" -ForegroundColor Yellow

if (-not $DryRun -and $filesFixed -gt 0) {
    Write-Host "✅ Fixed $filesFixed files" -ForegroundColor Green
}

# Generate report
$report = @{
    Timestamp = Get-Date -Format 'o'
    DryRun = $DryRun
    TotalFiles = $htmlFiles.Count
    MissingViewport = $missingViewport.Count
    FilesFixed = $filesFixed
    Files = $missingViewport | ForEach-Object { Split-Path $_ -Leaf }
}

$report | ConvertTo-Json -Depth 10 | Out-File $ReportPath -Encoding UTF8
Write-Host "📄 Report saved: $ReportPath" -ForegroundColor Gray

if ($DryRun) {
    Write-Host "`n⚠️  DRY RUN - No changes made. Run without -DryRun to apply fixes." -ForegroundColor Yellow
} else {
    Write-Host "`n✅ Viewport meta tags added successfully!" -ForegroundColor Green
}
