<#
.SYNOPSIS
    Fixes animation tier violations (T2/T3 on Level 1 pages)
.DESCRIPTION
    Ensures only T1 animations on Level 1 pages per glassmorphism standard
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"

# Level 1 pages (main navigation)
$level1Pages = @(
    "index.html",
    "getting-started.html",
    "faq.html"
)

$violations = @()
$filesFixed = 0

foreach ($page in $level1Pages) {
    $filePath = Join-Path $DocsRoot $page
    if (-not (Test-Path $filePath)) { continue }
    
    $content = Get-Content $filePath -Raw
    $originalContent = $content
    
    # Find T2/T3 violations
    if ($content -match 'animation-tier-[2-3]|data-animation-tier="[2-3]"') {
        $violations += $page
        
        if (-not $DryRun) {
            # Replace T2/T3 with T1
            $content = $content -replace 'animation-tier-2', 'animation-tier-1'
            $content = $content -replace 'animation-tier-3', 'animation-tier-1'
            $content = $content -replace 'data-animation-tier="2"', 'data-animation-tier="1"'
            $content = $content -replace 'data-animation-tier="3"', 'data-animation-tier="1"'
            
            if ($content -ne $originalContent) {
                $content | Out-File $filePath -Encoding UTF8 -NoNewline
                $filesFixed++
            }
        }
    }
}

if ($DryRun) {
    Write-Host "Would fix $($violations.Count) files: $($violations -join ', ')" -ForegroundColor Yellow
} else {
    Write-Host "✅ Fixed $filesFixed animation tier violations" -ForegroundColor Green
}
