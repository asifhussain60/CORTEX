<#
.SYNOPSIS
    UI Component Crawler - Discovers Blazor/React/Vue components and their patterns

.DESCRIPTION
    Area-specific crawler for UI components. Discovers:
    - Component structure (parent/child relationships)
    - Props/parameters (types, defaults, required)
    - DI injections (@inject, useContext)
    - Element IDs (id="..." attributes) - CRITICAL for Playwright
    - Naming conventions (PascalCase, kebab-case)
    - Routing patterns (@page directives)
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.PARAMETER WorkspaceRoot
    Absolute path to the project workspace root (e.g., "D:\PROJECTS\NOOR CANVAS")

.PARAMETER OutputPath
    Path where ui-results.json will be written (default: KDS/kds-brain/crawler-temp/ui-results.json)

.OUTPUTS
    ui-results.json - Structured JSON with component discoveries

.EXAMPLE
    .\ui-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS"
    
.NOTES
    Version: 1.0.0
    Author: KDS Multi-Threaded Crawler System
    Performance Target: <1.5 min for 300 components
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$WorkspaceRoot,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath
)

# Default output path if not provided
if (-not $OutputPath) {
    # Normalize workspace root and detect KDS location
    $normalizedRoot = $WorkspaceRoot.TrimEnd('\')
    if ($normalizedRoot -match '\\KDS$') {
        # Workspace IS KDS
        $OutputPath = "$normalizedRoot\kds-brain\crawler-temp\ui-results.json"
    } else {
        # KDS is inside workspace
        $OutputPath = "$normalizedRoot\KDS\kds-brain\crawler-temp\ui-results.json"
    }
}

# Start timer
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$startTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

Write-Host "🎨 UI Crawler Started" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceRoot" -ForegroundColor Gray
Write-Host "Output: $OutputPath" -ForegroundColor Gray

# Configuration
$componentPatterns = @("*.razor", "*.tsx", "*.jsx", "*.vue", "*.svelte")
$excludeDirs = @("node_modules", "bin", "obj", "dist", "build", ".next", "out")

# Initialize result structure
$result = @{
    area = "UI"
    scan_time = $startTime
    duration_seconds = 0
    workspace_root = $WorkspaceRoot
    components = @()
    patterns = @{
        component_structure = "unknown"
        di_pattern = "unknown"
        naming = "unknown"
    }
    statistics = @{
        total_components = 0
        total_element_ids = 0
        total_di_injections = 0
        total_routes = 0
    }
}

# Helper: Extract element IDs from file content
function Get-ElementIds {
    param([string]$Content)
    
    $ids = @()
    # Match id="..." or id='...'
    $matches = [regex]::Matches($Content, 'id\s*=\s*[''"]([^''"]+)[''"]')
    foreach ($match in $matches) {
        $id = $match.Groups[1].Value
        if ($id -and $id -notmatch '^\s*$') {
            $ids += $id
        }
    }
    return $ids | Select-Object -Unique
}

# Helper: Extract DI injections (Blazor @inject)
function Get-DIInjections {
    param([string]$Content)
    
    $injections = @()
    # Match @inject Type Name
    $matches = [regex]::Matches($Content, '@inject\s+(\S+)\s+(\S+)')
    foreach ($match in $matches) {
        $injections += @{
            type = $match.Groups[1].Value
            name = $match.Groups[2].Value
        }
    }
    return $injections
}

# Helper: Extract parameters (Blazor @parameter)
function Get-Parameters {
    param([string]$Content)
    
    $parameters = @()
    # Match [Parameter] public Type Name { get; set; }
    $matches = [regex]::Matches($Content, '\[Parameter\]\s+public\s+(\S+)\s+(\S+)\s*\{')
    foreach ($match in $matches) {
        $parameters += @{
            name = $match.Groups[2].Value
            type = $match.Groups[1].Value
            required = $Content -match "\[Parameter.*Required.*\].*$($match.Groups[2].Value)"
        }
    }
    return $parameters
}

# Helper: Extract routes (Blazor @page)
function Get-Routes {
    param([string]$Content)
    
    $routes = @()
    # Match @page "..."
    $matches = [regex]::Matches($Content, '@page\s+[''"]([^''"]+)[''"]')
    foreach ($match in $matches) {
        $routes += $match.Groups[1].Value
    }
    return $routes
}

# Helper: Detect naming convention
function Get-NamingConvention {
    param([string]$FileName)
    
    if ($FileName -match '^[A-Z][a-z]+([A-Z][a-z]+)+') {
        return "PascalCase"
    } elseif ($FileName -match '^[a-z]+(-[a-z]+)+') {
        return "kebab-case"
    } elseif ($FileName -match '^[a-z]+(_[a-z]+)+') {
        return "snake_case"
    } else {
        return "unknown"
    }
}

# Step 1: Discover all component files
Write-Host "`n[1/4] Discovering component files..." -ForegroundColor Yellow

$componentFiles = @()
foreach ($pattern in $componentPatterns) {
    $files = Get-ChildItem -Path $WorkspaceRoot -Filter $pattern -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            -not $exclude
        }
    $componentFiles += $files
}

Write-Host "  Found $($componentFiles.Count) component files" -ForegroundColor Green

# Step 2: Parse each component
Write-Host "`n[2/4] Parsing component structure..." -ForegroundColor Yellow

$namingConventions = @{}
$diPatterns = @{}

foreach ($file in $componentFiles) {
    Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        # Extract data
        $elementIds = Get-ElementIds -Content $content
        $diInjections = Get-DIInjections -Content $content
        $parameters = Get-Parameters -Content $content
        $routes = Get-Routes -Content $content
        $namingConvention = Get-NamingConvention -FileName $file.BaseName
        
        # Track patterns
        $namingConventions[$namingConvention] = ($namingConventions[$namingConvention] ?? 0) + 1
        if ($diInjections.Count -gt 0) {
            $diPatterns["inject-attribute"] = ($diPatterns["inject-attribute"] ?? 0) + 1
        }
        
        # Build component entry
        $component = @{
            path = $relativePath
            type = switch ($file.Extension) {
                ".razor" { "blazor-component" }
                ".tsx" { "react-typescript-component" }
                ".jsx" { "react-component" }
                ".vue" { "vue-component" }
                ".svelte" { "svelte-component" }
                default { "unknown" }
            }
            naming_convention = $namingConvention
            dependencies = @($diInjections | ForEach-Object { "@inject $($_.type) $($_.name)" })
            parameters = $parameters
            element_ids = $elementIds
            routes = $routes
        }
        
        $result.components += $component
        
        # Update statistics
        $result.statistics.total_element_ids += $elementIds.Count
        $result.statistics.total_di_injections += $diInjections.Count
        $result.statistics.total_routes += $routes.Count
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

$result.statistics.total_components = $result.components.Count

# Step 3: Detect patterns
Write-Host "`n[3/4] Detecting patterns..." -ForegroundColor Yellow

# Naming convention (most common)
$dominantNaming = ($namingConventions.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key
$result.patterns.naming = $dominantNaming ?? "unknown"

# DI pattern (most common)
$dominantDI = ($diPatterns.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key
$result.patterns.di_pattern = $dominantDI ?? "none"

# Component structure (heuristic based on folder depth)
$avgDepth = ($result.components | ForEach-Object {
    ($_.path -split '/').Count
}) | Measure-Object -Average | Select-Object -ExpandProperty Average

$result.patterns.component_structure = if ($avgDepth -gt 3) {
    "feature-based"  # Components organized by feature
} elseif ($avgDepth -gt 2) {
    "type-based"     # Components organized by type (Pages/, Components/, Shared/)
} else {
    "flat"           # All components in one folder
}

Write-Host "  Dominant naming: $($result.patterns.naming)" -ForegroundColor Green
Write-Host "  DI pattern: $($result.patterns.di_pattern)" -ForegroundColor Green
Write-Host "  Component structure: $($result.patterns.component_structure)" -ForegroundColor Green

# Step 4: Write output
Write-Host "`n[4/4] Writing output..." -ForegroundColor Yellow

$stopwatch.Stop()
$result.duration_seconds = [int]$stopwatch.Elapsed.TotalSeconds

# Ensure output directory exists
$outputDir = Split-Path -Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

# Write JSON
$result | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "`n✅ UI Crawler Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Components discovered: $($result.statistics.total_components)" -ForegroundColor White
Write-Host "Element IDs found: $($result.statistics.total_element_ids)" -ForegroundColor White
Write-Host "DI injections: $($result.statistics.total_di_injections)" -ForegroundColor White
Write-Host "Routes: $($result.statistics.total_routes)" -ForegroundColor White
Write-Host "Duration: $($result.duration_seconds)s" -ForegroundColor White
Write-Host "Output: $OutputPath" -ForegroundColor Gray
Write-Host "════════════════════════════════════" -ForegroundColor Cyan

# Return result object for orchestrator
return $result
