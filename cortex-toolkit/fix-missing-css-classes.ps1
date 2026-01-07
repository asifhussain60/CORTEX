<#
.SYNOPSIS
    Fixes missing CSS classes referenced in HTML
.DESCRIPTION
    Analyzes 734 missing classes and creates them or fixes typos
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$cssFiles = Get-ChildItem -Path (Join-Path $DocsRoot "assets\css") -Filter "*.css" -File
$htmlFiles = Get-ChildItem -Path $DocsRoot -Filter "*.html" -Recurse -File |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

# Load all CSS classes
$definedClasses = @{}
foreach ($cssFile in $cssFiles) {
    $cssContent = Get-Content $cssFile.FullName -Raw
    $matches = [regex]::Matches($cssContent, '\.([a-zA-Z0-9_-]+)\s*\{')
    foreach ($match in $matches) {
        $definedClasses[$match.Groups[1].Value] = $true
    }
}

Write-Host "Loaded $($definedClasses.Count) defined CSS classes" -ForegroundColor Cyan

# Find missing classes
$missingClasses = @{}
foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Extract class attributes
    $matches = [regex]::Matches($content, 'class="([^"]+)"')
    foreach ($match in $matches) {
        $classes = $match.Groups[1].Value -split '\s+' | Where-Object { $_ -match '\S' }
        foreach ($class in $classes) {
            if (-not $definedClasses.ContainsKey($class)) {
                if (-not $missingClasses.ContainsKey($class)) {
                    $missingClasses[$class] = @{
                        Count = 0
                        Files = @()
                    }
                }
                $missingClasses[$class].Count++
                if ($missingClasses[$class].Files -notcontains $file.FullName) {
                    $missingClasses[$class].Files += $file.FullName
                }
            }
        }
    }
}

Write-Host "Found $($missingClasses.Count) missing CSS classes" -ForegroundColor Yellow

# Categorize missing classes
$typos = @{}
$intentional = @{}
$compound = @{}

foreach ($class in $missingClasses.Keys) {
    # Check for compound selectors (used with other classes)
    if ($class -match '^[a-z]+-[a-z]+-[a-z]+') {
        $compound[$class] = $missingClasses[$class]
        continue
    }
    
    # Check for common typos (close matches to existing classes)
    $closeMatch = $definedClasses.Keys | Where-Object {
        $_ -like "*$($class.Substring(0, [Math]::Min(4, $class.Length)))*"
    } | Select-Object -First 1
    
    if ($closeMatch) {
        $typos[$class] = @{
            Suggestion = $closeMatch
            Data = $missingClasses[$class]
        }
    } else {
        $intentional[$class] = $missingClasses[$class]
    }
}

# Generate report
$report = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    TotalMissing = $missingClasses.Count
    Typos = $typos.Count
    Intentional = $intentional.Count
    Compound = $compound.Count
    Details = @{
        Typos = $typos
        Intentional = $intentional
        Compound = $compound
    }
}

$reportPath = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports\missing-css-classes-$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$report | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8

Write-Host "`n📊 Analysis Complete:" -ForegroundColor Cyan
Write-Host "   Typos: $($typos.Count) (suggest fixes)" -ForegroundColor Yellow
Write-Host "   Intentional: $($intentional.Count) (need CSS)" -ForegroundColor Magenta
Write-Host "   Compound: $($compound.Count) (framework classes)" -ForegroundColor Blue
Write-Host "`n📄 Report: $reportPath" -ForegroundColor Green

# Create stub CSS for intentional classes if not dry run
if (-not $DryRun -and $intentional.Count -gt 0) {
    $stubCss = "`n/* Auto-generated stubs for missing classes - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') */`n"
    
    foreach ($class in $intentional.Keys | Sort-Object) {
        $stubCss += "`n.$class {`n    /* TODO: Define styles for this class */`n    /* Used in $($intentional[$class].Count) locations */`n}`n"
    }
    
    $stubPath = Join-Path $DocsRoot "assets\css\missing-classes-stubs.css"
    $stubCss | Out-File $stubPath -Encoding UTF8
    
    Write-Host "✅ Created stub CSS: missing-classes-stubs.css" -ForegroundColor Green
}
