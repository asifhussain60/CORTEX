<#
.SYNOPSIS
    Defines real styles for 213 intentional CSS classes
.DESCRIPTION
    Converts stub classes to proper glassmorphism-compliant styles
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$stubFile = Join-Path $DocsRoot "assets\css\missing-classes-stubs.css"
$outputFile = Join-Path $DocsRoot "assets\css\intentional-classes.css"

if (-not (Test-Path $stubFile)) {
    Write-Host "❌ Stub file not found" -ForegroundColor Red
    exit 1
}

$stubContent = Get-Content $stubFile -Raw

# Define style templates based on class naming patterns
$styleTemplates = @{
    'antipattern-*' = @{
        'antipattern-header' = 'background: var(--glass-light); padding: var(--space-md); border-left: 3px solid var(--danger); margin-bottom: var(--space-sm);'
        'antipattern-detail' = 'padding: var(--space-md); background: var(--glass-lighter); border-radius: var(--radius-md);'
        'antipattern-list' = 'display: grid; gap: var(--space-md);'
        'antipattern-name' = 'font-weight: 600; color: var(--danger); font-size: 1.1rem;'
    }
    'badge-*' = @{
        'badge-critical' = 'background: var(--danger); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase;'
        'badge-info' = 'background: var(--info); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;'
        'badge-status' = 'background: var(--glass-light); padding: 4px 12px; border-radius: 12px; font-size: 0.75rem; border: 1px solid var(--border-color);'
    }
    'card-*' = @{
        'card-grid' = 'display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: var(--space-lg);'
        'card-header' = 'padding: var(--space-md); background: var(--glass-light); border-bottom: 1px solid var(--border-color);'
        'card-body' = 'padding: var(--space-md);'
        'card-footer' = 'padding: var(--space-md); background: var(--glass-lighter); border-top: 1px solid var(--border-color);'
    }
    'category-*' = @{
        'category-header' = 'font-size: 1.25rem; font-weight: 600; margin-bottom: var(--space-md); color: var(--primary);'
        'category-content' = 'padding: var(--space-md);'
    }
    'code-*' = @{
        'code-block' = 'background: var(--code-bg); padding: var(--space-md); border-radius: var(--radius-md); overflow-x: auto; font-family: var(--font-mono);'
        'code-header' = 'background: var(--glass-dark); padding: var(--space-sm) var(--space-md); border-radius: var(--radius-md) var(--radius-md) 0 0; font-size: 0.875rem;'
    }
    'icon-*' = @{
        'icon-wrapper' = 'display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: var(--radius-md); background: var(--glass-light);'
        'icon-large' = 'font-size: 2rem;'
        'icon-small' = 'font-size: 0.875rem;'
    }
    'metric-*' = @{
        'metric-card' = 'background: var(--glass-card); padding: var(--space-lg); border-radius: var(--radius-lg); border: 1px solid var(--border-color);'
        'metric-value' = 'font-size: 2rem; font-weight: 700; color: var(--primary);'
        'metric-label' = 'font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;'
    }
    'status-*' = @{
        'status-success' = 'color: var(--success); font-weight: 600;'
        'status-warning' = 'color: var(--warning); font-weight: 600;'
        'status-error' = 'color: var(--danger); font-weight: 600;'
        'status-info' = 'color: var(--info); font-weight: 600;'
    }
    'timeline-*' = @{
        'timeline-container' = 'position: relative; padding-left: var(--space-xl);'
        'timeline-item' = 'position: relative; padding-bottom: var(--space-lg); border-left: 2px solid var(--border-color);'
        'timeline-marker' = 'position: absolute; left: -6px; width: 12px; height: 12px; border-radius: 50%; background: var(--primary);'
    }
}

# Parse stub file and generate real styles
$newCss = "/* Glassmorphism-compliant styles for intentional classes - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') */`n`n"
$classesGenerated = 0

# Extract class names from stubs
$matches = [regex]::Matches($stubContent, '\.([a-zA-Z0-9_-]+)\s*\{')
foreach ($match in $matches) {
    $className = $match.Groups[1].Value
    
    # Skip invalid class names
    if ($className -match '[\$\{\}]|^:$|^''|^"') { continue }
    
    $styleGenerated = $false
    
    # Match against templates
    foreach ($pattern in $styleTemplates.Keys) {
        $patternRegex = $pattern -replace '\*', '.*'
        if ($className -match "^$patternRegex$") {
            foreach ($templateClass in $styleTemplates[$pattern].Keys) {
                if ($className -match "^$($templateClass -replace '\*', '.*')$") {
                    $newCss += ".$className {`n"
                    $styles = $styleTemplates[$pattern][$templateClass] -split ';' | Where-Object { $_ -match '\S' }
                    foreach ($style in $styles) {
                        $newCss += "    $($style.Trim());`n"
                    }
                    $newCss += "}`n`n"
                    $styleGenerated = $true
                    $classesGenerated++
                    break
                }
            }
            if ($styleGenerated) { break }
        }
    }
    
    # Generic fallback for unmatched classes
    if (-not $styleGenerated) {
        $newCss += ".$className {`n"
        $newCss += "    /* Generic glassmorphism style */`n"
        $newCss += "    padding: var(--space-md);`n"
        $newCss += "    background: var(--glass-light);`n"
        $newCss += "    border-radius: var(--radius-md);`n"
        $newCss += "}`n`n"
        $classesGenerated++
    }
}

if (-not $DryRun) {
    $newCss | Out-File $outputFile -Encoding UTF8
    Write-Host "✅ Generated $classesGenerated intentional classes in intentional-classes.css" -ForegroundColor Green
} else {
    Write-Host "Would generate $classesGenerated classes" -ForegroundColor Yellow
}
