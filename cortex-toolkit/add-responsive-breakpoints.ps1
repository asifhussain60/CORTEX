# add-responsive-breakpoints.ps1
# Adds mobile-first responsive breakpoints to HTML pages
# Part of CORTEX Glassmorphism Toolkit v4.3.0

param(
    [Parameter(Mandatory=$false)]
    [string]$Path = "docs/",
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoFix,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  📱 CORTEX Responsive Breakpoints Generator             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Standard breakpoints
$breakpoints = @{
    Mobile = 320
    Tablet = 768
    Desktop = 1024
    Large = 1440
}

Write-Host "📊 Standard Breakpoints:" -ForegroundColor Gray
foreach ($bp in $breakpoints.GetEnumerator() | Sort-Object Value) {
    Write-Host "   $($bp.Key): $($bp.Value)px" -ForegroundColor DarkGray
}
Write-Host ""

# Get all HTML files
$htmlFiles = if (Test-Path $Path -PathType Leaf) {
    @(Get-Item $Path)
} else {
    Get-ChildItem -Path $Path -Recurse -Filter "*.html"
}

Write-Host "📄 Processing $($htmlFiles.Count) HTML files...`n" -ForegroundColor Yellow

$filesUpdated = 0
$filesSkipped = 0

foreach ($file in $htmlFiles) {
    Write-Host "🔍 Checking: $($file.Name)" -ForegroundColor Gray
    
    $content = Get-Content $file.FullName -Raw
    $modified = $false
    
    # Check if responsive breakpoints already exist
    $hasBreakpoints = $content -match '@media\s*\(min-width:\s*768px\)' -or 
                      $content -match '@media\s*\(max-width:\s*768px\)'
    
    if ($hasBreakpoints) {
        Write-Host "  ✅ Already has responsive breakpoints" -ForegroundColor Green
        $filesSkipped++
        continue
    }
    
    if ($AutoFix) {
        # Generate comprehensive responsive CSS
        $responsiveCSS = @"


    /* ═══════════════════════════════════════════════════════════════
       RESPONSIVE BREAKPOINTS - Auto-Generated
       Mobile-First Design (320px → 1440px+)
       ═══════════════════════════════════════════════════════════════ */
    
    /* ━━━ BASE: Mobile First (320px+) ━━━ */
    /* Default styles above apply to mobile */
    
    body {
        font-size: 16px;
        line-height: 1.6;
        padding: var(--spacing-sm, 1rem);
    }
    
    .glass-card-display {
        padding: var(--spacing-md, 1.5rem);
        margin: var(--spacing-sm, 1rem) 0;
    }
    
    .masonry-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: var(--spacing-md, 1.5rem);
    }
    
    /* ━━━ TABLET: 768px+ ━━━ */
    @media (min-width: 768px) {
        body {
            padding: var(--spacing-md, 1.5rem);
        }
        
        .glass-card-display {
            padding: var(--spacing-lg, 2rem);
            margin: var(--spacing-md, 1.5rem) 0;
        }
        
        .masonry-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: var(--spacing-lg, 2rem);
        }
        
        .hero-robot-container svg {
            width: 200px;
            height: 200px;
        }
    }
    
    /* ━━━ DESKTOP: 1024px+ ━━━ */
    @media (min-width: 1024px) {
        .masonry-grid {
            grid-template-columns: repeat(3, 1fr);
        }
        
        .glass-card-display {
            padding: var(--spacing-xl, 2.5rem);
        }
    }
    
    /* ━━━ LARGE DESKTOP: 1440px+ ━━━ */
    @media (min-width: 1440px) {
        .masonry-grid {
            grid-template-columns: repeat(4, 1fr);
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
    }
    
    /* ━━━ PORTRAIT MODE (Mobile/Tablet) ━━━ */
    @media (orientation: portrait) and (max-width: 768px) {
        .hero-robot-container svg {
            width: 160px;
            height: 160px;
            transform: scale(0.8);
        }
        
        .hero-section-wrapper {
            margin-top: 1rem;
        }
        
        .glass-card-display h1 {
            font-size: clamp(1.75rem, 5vw, 2.5rem);
        }
    }
    
    /* ━━━ LANDSCAPE MODE (Short viewports) ━━━ */
    @media (orientation: landscape) and (max-height: 600px) {
        .hero-robot-container svg {
            width: 120px;
            height: 120px;
            transform: scale(0.6);
        }
        
        .hero-section-wrapper {
            margin-top: 0.5rem;
        }
        
        .glass-card-display {
            padding: var(--spacing-sm, 1rem);
        }
    }
    
    /* ━━━ MOBILE SPECIFIC: Max 767px ━━━ */
    @media (max-width: 767px) {
        /* Ensure no horizontal overflow */
        * {
            max-width: 100%;
            overflow-wrap: break-word;
            word-wrap: break-word;
        }
        
        img, svg, video {
            max-width: 100%;
            height: auto;
        }
        
        /* Stack navigation vertically */
        nav ul {
            flex-direction: column;
            gap: var(--spacing-sm, 1rem);
        }
        
        /* Larger touch targets */
        a:not(.robot-head-link),
        button,
        .glass-card-clickable {
            min-height: 48px;
            padding: 16px 20px;
        }
        
        /* Reduce hero size on small screens */
        .hero-description {
            font-size: 0.95rem;
        }
        
        /* Single column for all grids */
        .card-stats,
        .hero-stats {
            flex-direction: column;
            align-items: stretch;
        }
    }
    
    /* ━━━ TABLET SPECIFIC: 768px - 1023px ━━━ */
    @media (min-width: 768px) and (max-width: 1023px) {
        .masonry-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .glass-card-display {
            padding: var(--spacing-lg, 2rem);
        }
    }
"@
        
        # Insert before closing </style> tag or create style section
        if ($content -match '</style>') {
            $content = $content -replace '</style>', "$responsiveCSS`n</style>"
            $modified = $true
        } elseif ($content -match '</head>') {
            $content = $content -replace '</head>', "<style>$responsiveCSS`n</style>`n</head>"
            $modified = $true
        } else {
            Write-Host "  ⚠️  No <head> or <style> section found - skipping" -ForegroundColor Yellow
            continue
        }
        
        # Save changes
        if ($modified -and -not $DryRun) {
            Set-Content -Path $file.FullName -Value $content -NoNewline
            $filesUpdated++
            Write-Host "  ✅ Added responsive breakpoints (320px, 768px, 1024px, 1440px + orientations)" -ForegroundColor Green
        } elseif ($DryRun) {
            Write-Host "  💡 Would add responsive breakpoints" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ❌ Missing responsive breakpoints" -ForegroundColor Red
    }
}

# Summary Report
Write-Host "`n╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  📊 RESPONSIVE BREAKPOINTS SUMMARY                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

Write-Host "✅ Already compliant: $filesSkipped files" -ForegroundColor Green
Write-Host "📱 Needed updates: $($htmlFiles.Count - $filesSkipped) files" -ForegroundColor Yellow

if ($AutoFix -and -not $DryRun) {
    Write-Host "✅ Updated: $filesUpdated files`n" -ForegroundColor Green
    
    Write-Host "💡 Test responsive design:" -ForegroundColor Cyan
    Write-Host "   1. Open http://localhost:8000/" -ForegroundColor Gray
    Write-Host "   2. Press F12 → Toggle device toolbar (Ctrl+Shift+M)" -ForegroundColor Gray
    Write-Host "   3. Test breakpoints:" -ForegroundColor Gray
    Write-Host "      • 320px (Mobile - iPhone SE)" -ForegroundColor DarkGray
    Write-Host "      • 768px (Tablet - iPad)" -ForegroundColor DarkGray
    Write-Host "      • 1024px (Desktop)" -ForegroundColor DarkGray
    Write-Host "      • 1440px (Large Desktop)" -ForegroundColor DarkGray
    Write-Host "   4. Test portrait & landscape orientations`n" -ForegroundColor Gray
    
    exit 0
} elseif ($DryRun) {
    Write-Host "`n💡 Dry run complete. Use -AutoFix to apply changes." -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n💡 Use -AutoFix flag to add responsive breakpoints." -ForegroundColor Yellow
    Write-Host "`nExample:" -ForegroundColor Gray
    Write-Host "  .\add-responsive-breakpoints.ps1 -Path 'docs/' -AutoFix`n" -ForegroundColor Gray
    exit 1
}
