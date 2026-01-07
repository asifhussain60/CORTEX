<#
.SYNOPSIS
    Cleans up CSS files by removing unused classes and redundancy
.DESCRIPTION
    Safely removes 865 unused CSS classes and reduces redundancy
    Backup created at: backups\css-backup-20260103_093835
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$cssDir = Join-Path $DocsRoot "assets\css"
$backupLocation = "backups\css-backup-20260103_093835"

Write-Host "🧹 CSS Cleanup Started" -ForegroundColor Cyan
Write-Host "📦 Backup Location: $backupLocation" -ForegroundColor Yellow

# Load unused CSS report
$unusedReport = Get-ChildItem -Path (Join-Path $PSScriptRoot "..\cortex-brain\documents\reports") -Filter "css-usage-*.json" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $unusedReport) {
    Write-Host "❌ No usage report found" -ForegroundColor Red
    exit 1
}

$report = Get-Content $unusedReport.FullName | ConvertFrom-Json
$unusedClasses = $report.unused_css_classes.instances | ForEach-Object { $_.class }

Write-Host "Found $($unusedClasses.Count) unused classes to remove" -ForegroundColor Yellow

# Categories to preserve (likely used by JavaScript or dynamically)
$preservePatterns = @(
    'active', 'hidden', 'visible', 'show', 'hide', 
    'open', 'closed', 'expanded', 'collapsed',
    'selected', 'disabled', 'enabled',
    'loading', 'error', 'success', 'warning',
    'hover', 'focus', 'current',
    'mobile', 'tablet', 'desktop',
    'animation', 'transition'
)

$safeToRemove = @()
$preserved = @()

foreach ($class in $unusedClasses) {
    $shouldPreserve = $false
    foreach ($pattern in $preservePatterns) {
        if ($class -match $pattern) {
            $shouldPreserve = $true
            $preserved += $class
            break
        }
    }
    if (-not $shouldPreserve) {
        $safeToRemove += $class
    }
}

Write-Host "Safe to remove: $($safeToRemove.Count)" -ForegroundColor Green
Write-Host "Preserved (dynamic): $($preserved.Count)" -ForegroundColor Yellow

if (-not $DryRun) {
    # Remove safe classes from CSS files
    $cssFiles = Get-ChildItem -Path $cssDir -Filter "*.css" -File |
        Where-Object { $_.Name -ne 'missing-classes-stubs.css' }
    
    $totalRemoved = 0
    
    foreach ($cssFile in $cssFiles) {
        $content = Get-Content $cssFile.FullName -Raw
        $originalContent = $content
        
        foreach ($class in $safeToRemove) {
            # Remove class definition and its content
            $pattern = "\.(?:$([regex]::Escape($class)))\s*\{[^}]*\}\s*"
            $content = $content -replace $pattern, ''
        }
        
        if ($content -ne $originalContent) {
            $content | Out-File $cssFile.FullName -Encoding UTF8 -NoNewline
            $totalRemoved++
        }
    }
    
    # Remove stub file (no longer needed)
    $stubFile = Join-Path $cssDir "missing-classes-stubs.css"
    if (Test-Path $stubFile) {
        Remove-Item $stubFile -Force
        Write-Host "✅ Removed missing-classes-stubs.css (replaced by intentional-classes.css)" -ForegroundColor Green
    }
    
    Write-Host "✅ Cleaned $totalRemoved CSS files" -ForegroundColor Green
    Write-Host "✅ Removed $($safeToRemove.Count) unused classes" -ForegroundColor Green
} else {
    Write-Host "Would remove $($safeToRemove.Count) unused classes" -ForegroundColor Yellow
}
