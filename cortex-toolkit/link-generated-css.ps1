<#
.SYNOPSIS
    Links generated-classes.css to all HTML files
.DESCRIPTION
    Adds the generated-classes.css link to HTML files that reference inline-fix-* classes
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$htmlFiles = Get-ChildItem -Path $DocsRoot -Filter "*.html" -Recurse -File |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

$filesUpdated = 0
$cssLink = '<link rel="stylesheet" href="PATHPREFIX/assets/css/generated-classes.css">'

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Check if file uses inline-fix classes
    if ($content -match 'class="[^"]*inline-fix-') {
        # Check if already linked
        if ($content -notmatch 'generated-classes\.css') {
            # Calculate relative path depth
            $relativePath = $file.FullName.Replace($DocsRoot, '').TrimStart('\')
            $depth = ($relativePath -split '\\').Count - 1
            $pathPrefix = if ($depth -eq 0) { '.' } else { ('..' + '\..') * $depth -replace '\\', '/' }
            $pathPrefix = $pathPrefix -replace '\\', '/'
            
            $actualCssLink = $cssLink -replace 'PATHPREFIX', $pathPrefix
            
            if (-not $DryRun) {
                # Add after other CSS links or after <head>
                if ($content -match '(<link[^>]+stylesheet[^>]+>)\s*') {
                    $lastCssLink = $matches[0]
                    $content = $content -replace [regex]::Escape($lastCssLink), "$lastCssLink`n    $actualCssLink"
                } elseif ($content -match '(<head[^>]*>)') {
                    $content = $content -replace '(<head[^>]*>)', "`$1`n    $actualCssLink"
                }
                
                $content | Out-File $file.FullName -Encoding UTF8 -NoNewline
            }
            $filesUpdated++
        }
    }
}

Write-Host "$(if ($DryRun) {'Would update'} else {'Updated'}) $filesUpdated files" -ForegroundColor $(if ($DryRun) {'Yellow'} else {'Green'})
