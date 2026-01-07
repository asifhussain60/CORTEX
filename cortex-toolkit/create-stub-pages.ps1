<#
.SYNOPSIS
    Creates stub HTML pages for missing documentation links

.DESCRIPTION
    Analyzes broken links from docs-organizer report and creates placeholder
    stub pages with "Coming Soon" messages. Prevents future cleanup scripts
    from treating these as orphaned files.

.PARAMETER ReportPath
    Path to docs-cleanup JSON report (default: latest in cortex-brain/documents/reports/)

.PARAMETER DocsRoot
    Root directory of documentation (default: ../docs)

.PARAMETER DryRun
    Preview what would be created without making changes

.PARAMETER Force
    Skip confirmation prompts

.EXAMPLE
    .\create-stub-pages.ps1 -DryRun
    # Preview stub page creation

.EXAMPLE
    .\create-stub-pages.ps1 -Force
    # Create all stub pages without prompts

.NOTES
    Version: 1.0.0
    Author: CORTEX Toolkit Manager
    Part of: CORTEX 4.0 Documentation System
#>

[CmdletBinding()]
param(
    [string]$ReportPath = "",
    [string]$DocsRoot = "",
    [switch]$DryRun = $true,
    [switch]$Force = $false
)

# ============================================================================
# CONFIGURATION
# ============================================================================

if (-not $DocsRoot) {
    $DocsRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\docs")).Path
}

if (-not $ReportPath) {
    # Find latest cleanup report
    $reportsDir = Join-Path (Split-Path $PSScriptRoot -Parent) "cortex-brain\documents\reports"
    $latestReport = Get-ChildItem $reportsDir -Filter "docs-cleanup-*.json" | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -First 1
    
    if ($latestReport) {
        $ReportPath = $latestReport.FullName
    } else {
        Write-Error "No cleanup report found. Run docs-organizer.ps1 first."
        exit 1
    }
}

# Patterns to exclude from stub creation (external files, planned deletions)
$ExcludePatterns = @(
    'archives/',
    'cortex-lens-output/',
    'prototypes/home-redesign',
    'technical/orchestrators/',  # Old structure
    'orchestrators/planning-v5/'  # Planning v5 phases not yet implemented
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White",
        [string]$Prefix = ""
    )
    
    if ($Prefix) {
        Write-Host "$Prefix " -NoNewline -ForegroundColor $Color
        Write-Host $Message
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Get-PageTitle {
    param([string]$FilePath)
    
    # Extract meaningful title from file path
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($FilePath)
    $folder = Split-Path $FilePath -Parent
    
    # Convert kebab-case to Title Case
    $title = ($fileName -split '-' | ForEach-Object { 
        (Get-Culture).TextInfo.ToTitleCase($_) 
    }) -join ' '
    
    # Add context from folder
    if ($folder -match 'knowledge/([^/]+)') {
        $domain = $matches[1]
        $domainTitle = ($domain -split '-' | ForEach-Object { 
            (Get-Culture).TextInfo.ToTitleCase($_) 
        }) -join ' '
        return "$title - $domainTitle"
    } elseif ($folder -match 'security') {
        return "$title - Security"
    } elseif ($folder -match 'orchestrators') {
        return "$title - Orchestrators"
    } elseif ($folder -match 'architecture') {
        return "$title - Architecture"
    } elseif ($folder -match 'getting-started') {
        return "$title - Getting Started"
    } elseif ($folder -match 'features') {
        return "$title - Features"
    } elseif ($folder -match 'story') {
        return "$title - The Awakening"
    }
    
    return $title
}

function Get-CategoryFromPath {
    param([string]$FilePath)
    
    if ($FilePath -match 'knowledge/([^/]+)/') {
        $domain = $matches[1]
        return ($domain -split '-' | ForEach-Object { 
            (Get-Culture).TextInfo.ToTitleCase($_) 
        }) -join ' '
    } elseif ($FilePath -match '(security|orchestrators|architecture|story|features)/') {
        return (Get-Culture).TextInfo.ToTitleCase($matches[1])
    }
    
    return "Documentation"
}

function Get-BackLink {
    param([string]$FilePath)
    
    $folder = Split-Path $FilePath -Parent
    
    # Map to appropriate index/hub page
    if ($FilePath -match 'knowledge/([^/]+)/') {
        $domain = $matches[1]
        return "../$domain-hub.html"
    } elseif ($FilePath -match 'security/') {
        return "index.html"
    } elseif ($FilePath -match 'orchestrators/') {
        return "index.html"
    } elseif ($FilePath -match 'architecture/') {
        return "index.html"
    } elseif ($FilePath -match 'features/') {
        return "../index.html"
    } elseif ($FilePath -match 'getting-started/') {
        return "index.html"
    } elseif ($FilePath -match 'story/') {
        return "viewer.html"
    }
    
    return "../index.html"
}

function New-StubHtmlPage {
    param(
        [string]$FilePath,
        [string]$FullPath
    )
    
    $title = Get-PageTitle -FilePath $FilePath
    $category = Get-CategoryFromPath -FilePath $FilePath
    $backLink = Get-BackLink -FilePath $FilePath
    
    # Calculate relative depth for CSS paths
    $depth = ($FilePath -split '/').Count - 1
    $cssPrefix = if ($depth -eq 1) { "" } else { "../" * ($depth - 1) }
    
    $stubContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title - CORTEX</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="${cssPrefix}assets/css/variables.css?v=2026-01-03">
    <link rel="stylesheet" href="${cssPrefix}assets/css/main.css?v=2026-01-03">
    <style>
        .stub-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }
        
        .stub-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 3rem;
            max-width: 600px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        .stub-icon {
            font-size: 4rem;
            color: var(--accent-primary, #00d9ff);
            margin-bottom: 1.5rem;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .stub-title {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-primary, #ffffff);
        }
        
        .stub-category {
            font-size: 0.875rem;
            color: var(--accent-secondary, #ffd700);
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 1.5rem;
        }
        
        .stub-message {
            font-size: 1.125rem;
            line-height: 1.6;
            color: var(--text-secondary, rgba(255, 255, 255, 0.7));
            margin-bottom: 2rem;
        }
        
        .stub-back-link {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: var(--accent-primary, #00d9ff);
            color: var(--bg-primary, #0a0e27);
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stub-back-link:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 217, 255, 0.3);
        }
        
        .stub-metadata {
            margin-top: 2rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-size: 0.75rem;
            color: var(--text-tertiary, rgba(255, 255, 255, 0.5));
        }
    </style>
</head>
<body>
    <div class="stub-container">
        <div class="stub-card">
            <div class="stub-icon">
                <i class="fas fa-hammer"></i>
            </div>
            
            <div class="stub-category">$category</div>
            
            <h1 class="stub-title">$title</h1>
            
            <p class="stub-message">
                This page is currently under construction. We're working hard to bring you 
                comprehensive content, interactive visualizations, and practical examples.
            </p>
            
            <a href="$backLink" class="stub-back-link">
                <i class="fas fa-arrow-left"></i>
                Back to Overview
            </a>
            
            <div class="stub-metadata">
                <p>Page Status: <strong>Placeholder</strong></p>
                <p>Created: $(Get-Date -Format 'yyyy-MM-dd')</p>
                <p>Auto-generated by CORTEX Toolkit Manager</p>
            </div>
        </div>
    </div>
</body>
</html>
"@
    
    return $stubContent
}

# ============================================================================
# MAIN LOGIC
# ============================================================================

Write-ColorOutput "🧠 " "Cyan" "🧠"
Write-ColorOutput "🧠 CORTEX Stub Page Creator v1.0.0" "Cyan" "🧠"
Write-ColorOutput "⚙️ Mode: $(if ($DryRun) { 'DRY RUN (preview)' } else { 'EXECUTE' })" "Yellow" "⚙️"
Write-Host ""

# Load cleanup report
Write-ColorOutput "📊 Loading cleanup report..." "Cyan" "📊"
if (-not (Test-Path $ReportPath)) {
    Write-Error "Report not found: $ReportPath"
    exit 1
}

$report = Get-Content $ReportPath -Raw | ConvertFrom-Json
$brokenLinks = $report.Validation.BrokenLinks

Write-ColorOutput "  Found $($brokenLinks.Count) broken links" "Gray" "  📋"

# Extract unique missing targets
$missingFiles = $brokenLinks | 
    Select-Object -ExpandProperty To -Unique |
    Where-Object { 
        $file = $_
        # Exclude patterns
        $exclude = $false
        foreach ($pattern in $ExcludePatterns) {
            if ($file -like "*$pattern*") {
                $exclude = $true
                break
            }
        }
        -not $exclude
    } |
    Sort-Object

Write-ColorOutput "  $($missingFiles.Count) files need stub pages (after exclusions)" "Gray" "  📋"

if ($missingFiles.Count -eq 0) {
    Write-ColorOutput "✅ No stub pages needed!" "Green" "✅"
    exit 0
}

# Categorize by type
$categories = @{
    'WIP Level 2' = @($missingFiles | Where-Object { $_ -match 'knowledge/.+/.+\.html' })
    'Features' = @($missingFiles | Where-Object { $_ -match 'features/' })
    'Architecture' = @($missingFiles | Where-Object { $_ -match 'architecture/' })
    'Security' = @($missingFiles | Where-Object { $_ -match 'security/' })
    'Story' = @($missingFiles | Where-Object { $_ -match 'story/' })
    'Getting Started' = @($missingFiles | Where-Object { $_ -match 'getting-started/' })
    'Other' = @($missingFiles | Where-Object { 
        $_ -notmatch 'knowledge/.+/.+\.html' -and
        $_ -notmatch 'features/' -and
        $_ -notmatch 'architecture/' -and
        $_ -notmatch 'security/' -and
        $_ -notmatch 'story/' -and
        $_ -notmatch 'getting-started/'
    })
}

Write-Host ""
Write-ColorOutput "📂 Stub pages by category:" "Cyan" "📂"
foreach ($category in $categories.Keys | Sort-Object) {
    $count = $categories[$category].Count
    if ($count -gt 0) {
        Write-ColorOutput "  $category`: $count files" "Gray" "  📁"
    }
}

# Confirm before proceeding
if (-not $DryRun -and -not $Force) {
    Write-Host ""
    $response = Read-Host "Create $($missingFiles.Count) stub pages? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-ColorOutput "❌ Cancelled by user" "Yellow" "❌"
        exit 0
    }
}

Write-Host ""
Write-ColorOutput "🔧 Creating stub pages..." "Cyan" "🔧"

$created = 0
$skipped = 0
$errors = 0

foreach ($file in $missingFiles) {
    $fullPath = Join-Path $DocsRoot $file
    
    # Check if already exists
    if (Test-Path $fullPath) {
        $skipped++
        Write-ColorOutput "  ⏭️  Skipped (exists): $file" "Gray" "  ⏭️"
        continue
    }
    
    try {
        if (-not $DryRun) {
            # Create directory if needed
            $dir = Split-Path $fullPath -Parent
            if (-not (Test-Path $dir)) {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
            }
            
            # Generate and save stub content
            $stubContent = New-StubHtmlPage -FilePath $file -FullPath $fullPath
            Set-Content -Path $fullPath -Value $stubContent -Encoding UTF8
            
            Write-ColorOutput "  ✅ Created: $file" "Green" "  ✅"
        } else {
            Write-ColorOutput "  👁️  Would create: $file" "Cyan" "  👁️"
        }
        $created++
    } catch {
        $errors++
        Write-ColorOutput "  ❌ Error creating $file`: $_" "Red" "  ❌"
    }
}

Write-Host ""
Write-ColorOutput "✅ Stub Creation Complete!" "Green" "✅"
Write-Host ""
Write-Host "Summary:"
Write-ColorOutput "  ✅ Created: $created" "Green" "  ✅"
if ($skipped -gt 0) {
    Write-ColorOutput "  ⏭️  Skipped: $skipped" "Yellow" "  ⏭️"
}
if ($errors -gt 0) {
    Write-ColorOutput "  ❌ Errors: $errors" "Red" "  ❌"
}

if ($DryRun) {
    Write-Host ""
    Write-ColorOutput "💡 This was a dry run. Use -DryRun:`$false to create files." "Cyan" "💡"
}

Write-Host ""
Write-ColorOutput "🎉 All done!" "Green" "🎉"
