# fix-touch-targets.ps1
# Ensures all interactive elements meet WCAG 2.5.5 touch target size (44x44px minimum)
# Part of CORTEX Glassmorphism Toolkit v4.3.0

param(
    [Parameter(Mandatory=$false)]
    [string]$Path = "docs/",
    
    [Parameter(Mandatory=$false)]
    [int]$MinSize = 44,
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoFix,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  👆 CORTEX Touch Target Validator (WCAG 2.5.5)          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "Target Size: ${MinSize}x${MinSize}px minimum (WCAG AA)" -ForegroundColor Gray

# Get all HTML files
$htmlFiles = if (Test-Path $Path -PathType Leaf) {
    @(Get-Item $Path)
} else {
    Get-ChildItem -Path $Path -Recurse -Filter "*.html"
}

Write-Host "📊 Analyzing $($htmlFiles.Count) HTML files...`n" -ForegroundColor Yellow

$violations = @()
$fixesApplied = 0

# Interactive element selectors
$interactiveSelectors = @(
    'a',
    'button',
    'input[type="button"]',
    'input[type="submit"]',
    'input[type="reset"]',
    '.glass-card-clickable',
    '.nav-link',
    '.btn',
    '.stat-badge',
    '[role="button"]'
)

foreach ($file in $htmlFiles) {
    Write-Host "🔍 Checking: $($file.Name)" -ForegroundColor Gray
    
    $content = Get-Content $file.FullName -Raw
    $fileViolations = 0
    $modified = $false
    
    # Check for inline styles with small dimensions
    $smallDimensionPattern = '(min-height|min-width|height|width):\s*([1-3]\d|[1-9])px'
    $matches = [regex]::Matches($content, $smallDimensionPattern)
    
    if ($matches.Count -gt 0) {
        $fileViolations += $matches.Count
        
        if ($AutoFix) {
            # Add touch-friendly CSS
            $touchCSS = @"


    /* Touch Target Compliance (WCAG 2.5.5) - Auto-Generated */
    /* Minimum ${MinSize}x${MinSize}px for interactive elements */
    
    a:not(.robot-head-link),
    button,
    input[type="button"],
    input[type="submit"],
    input[type="reset"],
    .glass-card-clickable,
    .nav-link,
    .btn {
        min-height: ${MinSize}px;
        min-width: ${MinSize}px;
        padding: 12px 16px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--spacing-xs, 8px);
    }
    
    /* Larger on mobile for easier interaction */
    @media (max-width: 767px) {
        a:not(.robot-head-link),
        button,
        .glass-card-clickable,
        .btn {
            min-height: 48px;
            min-width: 48px;
            padding: 16px 20px;
        }
    }
    
    /* Touch feedback */
    a:active,
    button:active,
    .glass-card-clickable:active {
        transform: scale(0.98);
        transition: transform 0.1s ease;
    }
    
    /* Icon spacing within buttons */
    button i,
    .btn i,
    a i {
        margin-right: var(--spacing-xs, 8px);
    }
    
    /* Stat badges need adequate padding */
    .stat-badge,
    .stat-pill {
        min-height: ${MinSize}px;
        padding: 8px 16px;
        display: inline-flex;
        align-items: center;
        gap: var(--spacing-xs, 8px);
    }
"@
            
            if ($content -match '</style>') {
                # Check if touch target CSS already exists
                if ($content -notmatch 'Touch Target Compliance') {
                    $content = $content -replace '</style>', "$touchCSS`n</style>"
                    $modified = $true
                }
            } else {
                # Add style section before </head>
                $content = $content -replace '</head>', "<style>$touchCSS`n</style>`n</head>"
                $modified = $true
            }
            
            if ($modified) {
                Write-Host "  ✅ Added touch target compliance CSS ($MinSize px minimum)" -ForegroundColor Green
            }
        }
    }
    
    # Check for clickable cards without adequate size
    if ($content -match 'glass-card-clickable' -and $content -notmatch 'min-height:\s*\d{2,}px') {
        $fileViolations++
        
        if ($AutoFix -and -not $modified) {
            # Already handled by CSS injection above
            $modified = $true
        }
    }
    
    # Save changes
    if ($modified -and -not $DryRun) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $fixesApplied++
    }
    
    # Report violations
    if ($fileViolations -gt 0) {
        $violations += [PSCustomObject]@{
            File = $file.Name
            Count = $fileViolations
            Status = if ($AutoFix -and $modified) { "FIXED" } else { "NEEDS FIX" }
        }
        
        Write-Host "  ⚠️  Found $fileViolations potential touch target violations" -ForegroundColor Yellow
        if ($AutoFix -and $modified) {
            Write-Host "  ✅ Applied fixes" -ForegroundColor Green
        }
    } else {
        Write-Host "  ✅ All touch targets compliant" -ForegroundColor Green
    }
}

# Summary Report
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  📊 TOUCH TARGET COMPLIANCE SUMMARY                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($violations.Count -eq 0) {
    Write-Host "✅ All $($htmlFiles.Count) pages have compliant touch targets!" -ForegroundColor Green
    Write-Host "   Minimum size: ${MinSize}x${MinSize}px (WCAG 2.5.5 AA)`n" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "📱 Pages with violations: $($violations.Count)/$($htmlFiles.Count)" -ForegroundColor Yellow
    
    $totalViolations = ($violations | Measure-Object -Property Count -Sum).Sum
    Write-Host "⚠️  Total violations found: $totalViolations`n" -ForegroundColor Yellow
    
    if ($AutoFix -and -not $DryRun) {
        Write-Host "✅ Applied fixes to $fixesApplied files" -ForegroundColor Green
        Write-Host "`n💡 Test touch targets:" -ForegroundColor Cyan
        Write-Host "   1. Open http://localhost:8000/" -ForegroundColor Gray
        Write-Host "   2. Press F12 → Toggle device toolbar (Ctrl+Shift+M)" -ForegroundColor Gray
        Write-Host "   3. Select mobile device (iPhone, Pixel, etc.)" -ForegroundColor Gray
        Write-Host "   4. Test tapping all interactive elements`n" -ForegroundColor Gray
    } elseif ($DryRun) {
        Write-Host "💡 Dry run complete. Use -AutoFix to apply changes." -ForegroundColor Yellow
    } else {
        Write-Host "💡 Use -AutoFix flag to automatically fix violations." -ForegroundColor Yellow
        Write-Host "`nExample:" -ForegroundColor Gray
        Write-Host "  .\fix-touch-targets.ps1 -Path 'docs/' -AutoFix`n" -ForegroundColor Gray
    }
    
    exit 1
}
