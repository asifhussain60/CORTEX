# Font Awesome Icon Fix Script
# Adds missing 'fas' prefix to all Font Awesome icon classes
# Version: 1.0.0
# Author: Asif Hussain

$ErrorActionPreference = "Stop"

Write-Host "🔧 Font Awesome Icon Fix Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get all HTML files
$htmlFiles = Get-ChildItem -Path "docs" -Filter "*.html" -Recurse -File

$totalFiles = $htmlFiles.Count
$totalFixed = 0
$filesModified = 0

Write-Host "Found $totalFiles HTML files to process" -ForegroundColor Yellow
Write-Host ""

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
    $originalContent = $content
    $fileFixed = 0
    
    # Pattern 1: Fix icons with pulse-glow-glass--fast but missing fas
    # Match: class="pulse-glow-glass--fast fa-xxxxx"
    # Replace with: class="fas fa-xxxxx pulse-glow-glass--fast"
    $pattern1 = 'class="pulse-glow-glass--fast (fa-[a-z-]+)"'
    $replacement1 = 'class="fas $1 pulse-glow-glass--fast"'
    $matches1 = [regex]::Matches($content, $pattern1)
    $fileFixed += $matches1.Count
    $content = $content -replace $pattern1, $replacement1
    
    # Pattern 2: Fix icons with just fa-xxxxx class (no other classes)
    # Match: class="fa-xxxxx"
    # Replace with: class="fas fa-xxxxx"
    $pattern2 = 'class="(fa-[a-z-]+)"'
    $replacement2 = 'class="fas $1"'
    $matches2 = [regex]::Matches($content, $pattern2)
    $fileFixed += $matches2.Count
    $content = $content -replace $pattern2, $replacement2
    
    # Pattern 3: Fix icons with other classes before fa-xxxxx
    # Match: class="something fa-xxxxx"
    # Replace with: class="something fas fa-xxxxx"
    $pattern3 = 'class="([^"]*\s)(fa-[a-z-]+)([^"]*)"'
    $replacement3 = 'class="$1fas $2$3"'
    # Only apply if not already fixed
    if ($content -notmatch 'class="[^"]*\bfas\b[^"]*\bfa-') {
        $matches3 = [regex]::Matches($content, $pattern3)
        $fileFixed += $matches3.Count
        $content = $content -replace $pattern3, $replacement3
    }
    
    # Pattern 4: Fix duplicate fas (in case script runs twice)
    # Match: class="fas fas fa-xxxxx"
    # Replace with: class="fas fa-xxxxx"
    $content = $content -replace 'class="fas fas ', 'class="fas '
    
    # Pattern 5: Fix icons with fa-xxxxx inside other attributes
    # Match: class="other-class fa-xxxxx another-class"
    # Replace with: class="other-class fas fa-xxxxx another-class"
    $pattern5 = 'class="([^"]*?)(?<!fas\s)(fa-[a-z-]+)([^"]*)"'
    $replacement5 = 'class="$1fas $2$3"'
    # Apply pattern 5 multiple times to catch all instances
    while ($content -match $pattern5 -and $content -notmatch 'class="[^"]*\bfas\b\s+\bfa-[a-z-]+') {
        $content = $content -replace $pattern5, $replacement5
    }
    
    if ($content -ne $originalContent) {
        # Backup original file
        $backupPath = $file.FullName + ".bak"
        Copy-Item -Path $file.FullName -Destination $backupPath -Force
        
        # Write fixed content
        Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
        
        $filesModified++
        $totalFixed += $fileFixed
        Write-Host "✅ Fixed $($file.FullName -replace [regex]::Escape($PWD), '.'): $fileFixed icons" -ForegroundColor Green
    } else {
        Write-Host "⏭️  Skipped $($file.FullName -replace [regex]::Escape($PWD), '.'): No icons to fix" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✨ Summary:" -ForegroundColor Cyan
Write-Host "   Files scanned: $totalFiles" -ForegroundColor White
Write-Host "   Files modified: $filesModified" -ForegroundColor Yellow
Write-Host "   Total icons fixed: $totalFixed" -ForegroundColor Green
Write-Host ""
Write-Host "💾 Backups created with .bak extension" -ForegroundColor Magenta
Write-Host "🔍 To verify, check any HTML file for 'class=\"fas fa-xxxxx\"'" -ForegroundColor Cyan
Write-Host ""
