<#
.SYNOPSIS
    UI Component Crawler - Discovers Blazor/React/Vue/Angular/AngularJS components and their patterns

.DESCRIPTION
    Area-specific crawler for UI components. Discovers:
    - Component structure (parent/child relationships)
    - Props/parameters (types, defaults, required)
    - DI injections (@inject, useContext, Angular DI, AngularJS $inject)
    - Element IDs (id="..." attributes) - CRITICAL for Playwright
    - Naming conventions (PascalCase, kebab-case)
    - Routing patterns (@page directives, Angular routes, AngularJS routes)
    - Modern frameworks: Angular (2+), React, Vue, Blazor, Svelte
    - Legacy: AngularJS (1.x)
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.PARAMETER WorkspaceRoot
    Absolute path to the project workspace root (e.g., "D:\PROJECTS\NOOR CANVAS")

.PARAMETER OutputPath
    Path where ui-results.json will be written (default: KDS/cortex-brain/crawler-temp/ui-results.json)

.OUTPUTS
    ui-results.json - Structured JSON with component discoveries

.EXAMPLE
    .\ui-crawler.ps1 -WorkspaceRoot "D:\PROJECTS\NOOR CANVAS"
    
.NOTES
    Version: 2.0.0 (Added Angular, React, Blazor enhanced detection)
    Author: KDS Multi-Threaded Crawler System
    Performance Target: <2 min for 2000+ files (includes multi-framework scanning)
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
        $OutputPath = "$normalizedRoot\cortex-brain\crawler-temp\ui-results.json"
    } else {
        # KDS is inside workspace
        $OutputPath = "$normalizedRoot\KDS\cortex-brain\crawler-temp\ui-results.json"
    }
}

# Start timer
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$startTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

Write-Host "🎨 UI Crawler Started" -ForegroundColor Cyan
Write-Host "Workspace: $WorkspaceRoot" -ForegroundColor Gray
Write-Host "Output: $OutputPath" -ForegroundColor Gray

# Configuration
$componentPatterns = @(
    "*.razor",      # Blazor
    "*.tsx",        # React TypeScript
    "*.jsx",        # React JavaScript
    "*.vue",        # Vue.js
    "*.svelte",     # Svelte
    "*.ts",         # Angular TypeScript components (will filter by @Component decorator)
    "*.html"        # Angular HTML templates (will pair with component files)
)
$excludeDirs = @("node_modules", "bin", "obj", "dist", "build", ".next", "out")

# Framework detection state
$angularJSDetected = $false
$angularJSFiles = @()
$angularDetected = $false  # Modern Angular (2+)
$angularFiles = @()
$reactDetected = $false
$blazorDetected = $false

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

# Helper: Detect if file is AngularJS component
function Test-IsAngularJSFile {
    param([string]$Content)
    
    # Check for AngularJS patterns
    $patterns = @(
        'angular\.module\(',
        '\.controller\(',
        '\.directive\(',
        '\.service\(',
        '\.factory\(',
        '\.filter\(',
        '\$scope',
        '\$http',
        '\$rootScope',
        '\$inject'
    )
    
    foreach ($pattern in $patterns) {
        if ($Content -match $pattern) {
            return $true
        }
    }
    
    return $false
}

# Helper: Detect if file is modern Angular component
function Test-IsAngularFile {
    param([string]$Content)
    
    # Check for Angular (2+) patterns
    $patterns = @(
        '@Component\(',
        '@NgModule\(',
        '@Injectable\(',
        '@Directive\(',
        '@Pipe\(',
        'import.*from\s+[''"]@angular/',
        'export\s+class.*Component'
    )
    
    foreach ($pattern in $patterns) {
        if ($Content -match $pattern) {
            return $true
        }
    }
    
    return $false
}

# Helper: Detect React patterns
function Test-IsReactFile {
    param([string]$Content)
    
    # Check for React patterns
    $patterns = @(
        'import\s+React',
        'from\s+[''"]react[''"]',
        'useState\(',
        'useEffect\(',
        'React\.Component',
        'React\.FC',
        'export\s+(?:default\s+)?function.*\(',
        'const.*=.*\(.*\)\s*=>'
    )
    
    foreach ($pattern in $patterns) {
        if ($Content -match $pattern) {
            return $true
        }
    }
    
    return $false
}

# Helper: Extract AngularJS module name
function Get-AngularJSModuleName {
    param([string]$Content)
    
    if ($Content -match 'angular\.module\([''"]([^''"]+)[''"]') {
        return $Matches[1]
    }
    return $null
}

# Helper: Extract AngularJS component type
function Get-AngularJSComponentType {
    param([string]$Content)
    
    if ($Content -match '\.controller\(') { return "angularjs-controller" }
    if ($Content -match '\.directive\(') { return "angularjs-directive" }
    if ($Content -match '\.service\(') { return "angularjs-service" }
    if ($Content -match '\.factory\(') { return "angularjs-factory" }
    if ($Content -match '\.filter\(') { return "angularjs-filter" }
    if ($Content -match '\.component\(') { return "angularjs-component" }
    if ($Content -match 'angular\.module\(') { return "angularjs-module" }
    
    return "angularjs-unknown"
}

# Helper: Extract AngularJS dependencies (DI)
function Get-AngularJSDependencies {
    param([string]$Content)
    
    $dependencies = @()
    
    # Match function(...dependencies) pattern
    if ($Content -match 'function\s*\(([^\)]*)\)') {
        $params = $Matches[1] -split ',' | ForEach-Object { $_.Trim() }
        $dependencies += $params | Where-Object { $_ -match '^\$' }  # AngularJS services start with $
    }
    
    # Match $inject array pattern
    if ($Content -match '\$inject\s*=\s*\[(.*?)\]') {
        $injected = $Matches[1] -split ',' | ForEach-Object { 
            $_.Trim().Trim('"').Trim("'") 
        }
        $dependencies += $injected
    }
    
    return $dependencies | Select-Object -Unique
}

# Step 0: Detect AngularJS presence
Write-Host "`n[0/5] Detecting UI frameworks..." -ForegroundColor Yellow

# Method 1: Look for package.json dependencies
$packageJsonFiles = Get-ChildItem -Path $WorkspaceRoot -Filter "package.json" -Recurse -File -ErrorAction SilentlyContinue |
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

foreach ($packageJson in $packageJsonFiles) {
    try {
        $content = Get-Content -Path $packageJson.FullName -Raw | ConvertFrom-Json
        
        # Check for AngularJS (1.x)
        if ($content.dependencies.angular -or $content.dependencies.PSObject.Properties.Name -contains 'angular') {
            $angularJSDetected = $true
            Write-Host "  ✅ AngularJS detected via package.json: $($packageJson.Directory.Name)" -ForegroundColor Green
        }
        
        # Check for modern Angular (2+)
        if ($content.dependencies.'@angular/core') {
            $angularDetected = $true
            $angularVersion = $content.dependencies.'@angular/core'
            Write-Host "  ✅ Angular $angularVersion detected via package.json" -ForegroundColor Green
        }
        
        # Check for React
        if ($content.dependencies.'react') {
            $reactDetected = $true
            $reactVersion = $content.dependencies.'react'
            Write-Host "  ✅ React $reactVersion detected via package.json" -ForegroundColor Green
        }
    } catch {
        # Ignore parse errors
    }
}

# Check for Blazor
$blazorFiles = Get-ChildItem -Path $WorkspaceRoot -Filter "*.razor" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
if ($blazorFiles) {
    $blazorDetected = $true
    Write-Host "  ✅ Blazor detected via .razor files" -ForegroundColor Green
}

# Method 2: Look for bower.json or bower_components/angular
if (-not $angularJSDetected) {
    $bowerJson = Get-ChildItem -Path $WorkspaceRoot -Filter "bower.json" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
    $bowerAngular = Get-ChildItem -Path $WorkspaceRoot -Filter "angular" -Directory -Recurse -ErrorAction SilentlyContinue | 
        Where-Object { $_.FullName -match "bower_components" } | Select-Object -First 1
    
    if ($bowerJson -or $bowerAngular) {
        $angularJSDetected = $true
        Write-Host "  ✅ AngularJS detected via Bower: $($bowerJson.Directory.Name ?? $bowerAngular.Parent.Name)" -ForegroundColor Green
    }
}

# Method 3: Sample JS files for AngularJS patterns (fallback)
if (-not $angularJSDetected) {
    Write-Host "  🔍 Sampling JS files for AngularJS patterns..." -ForegroundColor Yellow
    
    $jsFiles = Get-ChildItem -Path $WorkspaceRoot -Filter "*.js" -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            
            if ($_.Name -match '\.min\.js$') { $exclude = $true }
            if ($_.Name -match '^(jquery|bootstrap|lodash|moment)') { $exclude = $true }
            
            -not $exclude
        }
    
    # Sample first 20 files for quick detection
    $sampleSize = [Math]::Min(20, $jsFiles.Count)
    $sampledFiles = $jsFiles | Select-Object -First $sampleSize
    
    foreach ($file in $sampledFiles) {
        try {
            $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
            if (Test-IsAngularJSFile -Content $content) {
                $angularJSDetected = $true
                Write-Host "  ✅ AngularJS detected via code sampling" -ForegroundColor Green
                break
            }
        } catch {
            # Ignore read errors
        }
    }
}

# Method 4: Sample TypeScript files for modern Angular
if (-not $angularDetected) {
    Write-Host "  🔍 Sampling TS files for Angular patterns..." -ForegroundColor Yellow
    
    $tsFiles = Get-ChildItem -Path $WorkspaceRoot -Filter "*.ts" -Recurse -File -ErrorAction SilentlyContinue |
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
        } | Select-Object -First 20
    
    foreach ($file in $tsFiles) {
        try {
            $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
            if (Test-IsAngularFile -Content $content) {
                $angularDetected = $true
                Write-Host "  ✅ Angular detected via code sampling" -ForegroundColor Green
                break
            }
        } catch {
            # Ignore read errors
        }
    }
}

# If AngularJS detected, scan for .js files
if ($angularJSDetected) {
    Write-Host "  🔍 Scanning for AngularJS component files..." -ForegroundColor Yellow
    
    $jsFiles = Get-ChildItem -Path $WorkspaceRoot -Filter "*.js" -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            
            # Exclude common non-component directories
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            
            # Exclude minified files
            if ($_.Name -match '\.min\.js$') {
                $exclude = $true
            }
            
            # Exclude common library files
            if ($_.Name -match '^(jquery|angular|bootstrap|lodash|moment)') {
                $exclude = $true
            }
            
            -not $exclude
        }
    
    Write-Host "  📊 Scanning $($jsFiles.Count) JS files for AngularJS patterns..." -ForegroundColor Cyan
    
    $processedCount = 0
    foreach ($file in $jsFiles) {
        try {
            $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
            if (Test-IsAngularJSFile -Content $content) {
                $angularJSFiles += $file
            }
            
            $processedCount++
            if ($processedCount % 100 -eq 0) {
                Write-Host "    Processed $processedCount/$($jsFiles.Count) files..." -ForegroundColor Gray
            }
        } catch {
            # Ignore read errors
        }
    }
    
    Write-Host "  ✅ Found $($angularJSFiles.Count) AngularJS component files" -ForegroundColor Green
}

# If modern Angular detected, scan for .ts component files
if ($angularDetected) {
    Write-Host "  🔍 Scanning for Angular component files..." -ForegroundColor Yellow
    
    $tsFiles = Get-ChildItem -Path $WorkspaceRoot -Filter "*.ts" -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            $exclude = $false
            
            foreach ($dir in $excludeDirs) {
                if ($path -match "\\$dir\\") {
                    $exclude = $true
                    break
                }
            }
            
            # Exclude spec and test files
            if ($_.Name -match '\.(spec|test)\.ts$') {
                $exclude = $true
            }
            
            -not $exclude
        }
    
    Write-Host "  📊 Scanning $($tsFiles.Count) TS files for Angular components..." -ForegroundColor Cyan
    
    $processedCount = 0
    foreach ($file in $tsFiles) {
        try {
            $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
            if (Test-IsAngularFile -Content $content) {
                $angularFiles += $file
            }
            
            $processedCount++
            if ($processedCount % 100 -eq 0) {
                Write-Host "    Processed $processedCount/$($tsFiles.Count) files..." -ForegroundColor Gray
            }
        } catch {
            # Ignore read errors
        }
    }
    
    Write-Host "  ✅ Found $($angularFiles.Count) Angular component files" -ForegroundColor Green
}

if (-not $angularJSDetected -and -not $angularDetected -and -not $reactDetected -and -not $blazorDetected) {
    Write-Host "  ℹ️  No specific framework detected - scanning all modern framework patterns" -ForegroundColor Gray
}

# Step 1: Discover all component files
Write-Host "`n[1/5] Discovering component files..." -ForegroundColor Yellow

$componentFiles = @()

# Modern frameworks (Blazor, React, Vue, Svelte)
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

# Add AngularJS files if detected
$componentFiles += $angularJSFiles

# Add Angular files if detected
$componentFiles += $angularFiles

$modernCount = $componentFiles.Count - $angularJSFiles.Count - $angularFiles.Count
Write-Host "  Modern frameworks (Blazor/React/Vue): $modernCount" -ForegroundColor Green
if ($angularFiles.Count -gt 0) {
    Write-Host "  Angular components: $($angularFiles.Count)" -ForegroundColor Green
}
if ($angularJSFiles.Count -gt 0) {
    Write-Host "  AngularJS components: $($angularJSFiles.Count)" -ForegroundColor Green
}
Write-Host "  Total: $($componentFiles.Count) component files" -ForegroundColor Cyan

# Step 2: Parse each component
Write-Host "`n[2/5] Parsing component structure..." -ForegroundColor Yellow

$namingConventions = @{}
$diPatterns = @{}
$frameworkTypes = @{}

foreach ($file in $componentFiles) {
    Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        
        # Determine component type
        $componentType = "unknown"
        $dependencies = @()
        
        if ($file.Extension -eq ".js") {
            # AngularJS file
            $componentType = Get-AngularJSComponentType -Content $content
            $dependencies = Get-AngularJSDependencies -Content $content
            $moduleName = Get-AngularJSModuleName -Content $content
            
            $frameworkTypes["angularjs"] = ($frameworkTypes["angularjs"] ?? 0) + 1
            
            if ($dependencies.Count -gt 0) {
                $diPatterns["angularjs-di"] = ($diPatterns["angularjs-di"] ?? 0) + 1
            }
            
        } elseif ($file.Extension -eq ".ts" -and (Test-IsAngularFile -Content $content)) {
            # Modern Angular component
            $componentType = "angular-component"
            
            # Extract Angular-specific patterns
            if ($content -match '@Component\(\{([^}]+)\}\)') {
                $componentMeta = $Matches[1]
                
                # Extract selector
                if ($componentMeta -match 'selector:\s*[''"]([^''"]+)[''"]') {
                    $selector = $Matches[1]
                }
                
                # Extract template URL
                if ($componentMeta -match 'templateUrl:\s*[''"]([^''"]+)[''"]') {
                    $templateUrl = $Matches[1]
                }
            }
            
            # Extract constructor dependencies (DI)
            if ($content -match 'constructor\((.*?)\)') {
                $constructorParams = $Matches[1]
                $dependencies = @($constructorParams -split ',' | ForEach-Object {
                    if ($_ -match '(?:private|public|protected)?\s*(\w+):\s*(\w+)') {
                        "DI: $($Matches[2]) $($Matches[1])"
                    }
                })
            }
            
            $frameworkTypes["angular"] = ($frameworkTypes["angular"] ?? 0) + 1
            
            if ($dependencies.Count -gt 0) {
                $diPatterns["constructor-di"] = ($diPatterns["constructor-di"] ?? 0) + 1
            }
            
        } else {
            # Modern framework (Blazor, React, Vue, Svelte)
            $componentType = switch ($file.Extension) {
                ".razor" { "blazor-component" }
                ".tsx" { "react-typescript-component" }
                ".jsx" { "react-component" }
                ".vue" { "vue-component" }
                ".svelte" { "svelte-component" }
                default { "unknown" }
            }
            
            # Extract framework-specific data
            $diInjections = Get-DIInjections -Content $content
            $parameters = Get-Parameters -Content $content
            $routes = Get-Routes -Content $content
            $dependencies = @($diInjections | ForEach-Object { "@inject $($_.type) $($_.name)" })
            
            $frameworkKey = $componentType -replace '-.*$', ''
            $frameworkTypes[$frameworkKey] = ($frameworkTypes[$frameworkKey] ?? 0) + 1
            
            if ($diInjections.Count -gt 0) {
                $diPatterns["inject-attribute"] = ($diPatterns["inject-attribute"] ?? 0) + 1
            }
        }
        
        # Extract common data (works for all frameworks)
        $elementIds = Get-ElementIds -Content $content
        $namingConvention = Get-NamingConvention -FileName $file.BaseName
        
        # Track patterns
        $namingConventions[$namingConvention] = ($namingConventions[$namingConvention] ?? 0) + 1
        
        # Build component entry
        $component = @{
            path = $relativePath
            type = $componentType
            naming_convention = $namingConvention
            dependencies = $dependencies
            element_ids = $elementIds
        }
        
        # Add framework-specific fields
        if ($file.Extension -ne ".js") {
            $component.parameters = $parameters
            $component.routes = $routes
        } else {
            # AngularJS-specific fields
            if ($moduleName) {
                $component.module = $moduleName
            }
        }
        
        $result.components += $component
        
        # Update statistics
        $result.statistics.total_element_ids += $elementIds.Count
        $result.statistics.total_di_injections += $dependencies.Count
        if ($file.Extension -ne ".js" -and $routes) {
            $result.statistics.total_routes += $routes.Count
        }
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

$result.statistics.total_components = $result.components.Count

# Step 3: Detect patterns
Write-Host "`n[3/5] Detecting patterns..." -ForegroundColor Yellow

# Determine primary framework
$primaryFramework = ($frameworkTypes.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key
$result.patterns.primary_framework = $primaryFramework ?? "unknown"

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

Write-Host "  Primary framework: $($result.patterns.primary_framework)" -ForegroundColor Green
Write-Host "  Dominant naming: $($result.patterns.naming)" -ForegroundColor Green
Write-Host "  DI pattern: $($result.patterns.di_pattern)" -ForegroundColor Green
Write-Host "  Component structure: $($result.patterns.component_structure)" -ForegroundColor Green

# Step 4: Write output
Write-Host "`n[4/5] Writing output..." -ForegroundColor Yellow

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
