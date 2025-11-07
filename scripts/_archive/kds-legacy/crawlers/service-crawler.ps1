<#
.SYNOPSIS
    Service Crawler - Discovers business logic services and DI patterns

.DESCRIPTION
    Area-specific crawler for services/repositories. Discovers:
    - Service interfaces vs implementations
    - DI registration patterns
    - Business logic patterns
    - External dependencies
    
    Part of KDS v6.0 Multi-Threaded Crawler Architecture (Phase 2)

.NOTES
    Version: 1.0.0
    Performance Target: <1 min for 150 services
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
        $OutputPath = "$normalizedRoot\cortex-brain\crawler-temp\service-results.json"
    } else {
        # KDS is inside workspace
        $OutputPath = "$normalizedRoot\KDS\cortex-brain\crawler-temp\service-results.json"
    }
}

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$startTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

Write-Host "⚙️ Service Crawler Started" -ForegroundColor Cyan

$servicePatterns = @("*Service.cs", "*Repository.cs", "*Manager.cs", "services/*.ts", "services/*.js")
$excludeDirs = @("node_modules", "bin", "obj", "dist")

$result = @{
    area = "Services"
    scan_time = $startTime
    duration_seconds = 0
    workspace_root = $WorkspaceRoot
    services = @()
    patterns = @{
        di_registration = "unknown"
        naming = "unknown"
        layering = "unknown"
    }
    statistics = @{
        total_services = 0
        total_interfaces = 0
        total_di_registrations = 0
    }
}

# Helper: Extract interface name
function Get-InterfaceName {
    param([string]$Content, [string]$ClassName)
    
    $match = [regex]::Match($Content, "class\s+$ClassName\s*:\s*(\w+)")
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

# Helper: Extract constructor dependencies
function Get-Dependencies {
    param([string]$Content)
    
    $deps = @()
    # Match constructor parameters
    $match = [regex]::Match($Content, 'public\s+\w+\((.*?)\)', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    if ($match.Success) {
        $params = $match.Groups[1].Value -split ','
        foreach ($param in $params) {
            if ($param -match '(\w+)\s+\w+\s*$') {
                $deps += $matches[1]
            }
        }
    }
    return $deps
}

# Helper: Classify service pattern
function Get-ServicePattern {
    param([string]$FileName)
    
    if ($FileName -match 'Repository') { return "repository" }
    if ($FileName -match 'Manager') { return "manager" }
    if ($FileName -match 'Service') { return "service" }
    return "unknown"
}

# Step 1: Discover services
Write-Host "`n[1/3] Discovering services..." -ForegroundColor Yellow

$serviceFiles = @()
foreach ($pattern in $servicePatterns) {
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
    $serviceFiles += $files
}

Write-Host "  Found $($serviceFiles.Count) service files" -ForegroundColor Green

# Step 2: Parse services
Write-Host "`n[2/3] Parsing service structure..." -ForegroundColor Yellow

$namingPatterns = @{}
$servicePatternCounts = @{}

foreach ($file in $serviceFiles) {
    Write-Host "  Processing: $($file.Name)" -ForegroundColor Gray
    
    try {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
        $relativePath = $file.FullName.Replace("$WorkspaceRoot\", "").Replace("\", "/")
        $className = $file.BaseName
        
        $interface = Get-InterfaceName -Content $content -ClassName $className
        $dependencies = Get-Dependencies -Content $content
        $pattern = Get-ServicePattern -FileName $file.Name
        
        if ($interface -and $interface -match '^I[A-Z]') {
            $namingPatterns["I{Name} interface"] = ($namingPatterns["I{Name} interface"] ?? 0) + 1
            $result.statistics.total_interfaces++
        }
        
        $servicePatternCounts[$pattern] = ($servicePatternCounts[$pattern] ?? 0) + 1
        
        $service = @{
            path = $relativePath
            interface = $interface
            implementation = $className
            di_lifetime = "Scoped"  # Default assumption
            dependencies = $dependencies
            patterns = @($pattern)
        }
        
        $result.services += $service
        $result.statistics.total_services++
        
    } catch {
        Write-Warning "  Failed to parse $($file.Name): $_"
    }
}

# Step 3: Detect patterns
Write-Host "`n[3/3] Detecting patterns..." -ForegroundColor Yellow

$result.patterns.naming = ($namingPatterns.GetEnumerator() | Sort-Object -Property Value -Descending | Select-Object -First 1).Key ?? "unknown"
$result.patterns.di_registration = "Program.cs"  # C# standard
$result.patterns.layering = if ($servicePatternCounts["repository"] -gt 0 -and $servicePatternCounts["service"] -gt 0) {
    "repository-service-manager"
} else {
    "service-only"
}

$stopwatch.Stop()
$result.duration_seconds = [int]$stopwatch.Elapsed.TotalSeconds

$outputDir = Split-Path -Path $OutputPath -Parent
if (-not (Test-Path $outputDir)) {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

$result | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8

Write-Host "`n✅ Service Crawler Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Services: $($result.statistics.total_services)" -ForegroundColor White
Write-Host "Interfaces: $($result.statistics.total_interfaces)" -ForegroundColor White
Write-Host "Duration: $($result.duration_seconds)s" -ForegroundColor White
Write-Host "════════════════════════════════════" -ForegroundColor Cyan

return $result
