#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick CORTEX cleanup command + Old manifest removal
    
.DESCRIPTION
    1. Removes old manifest files (planning-system-*.yaml with version <4.0)
    2. Executes the CORTEX holistic cleanup orchestrator
    Shortcut for: python scripts/cli_wrappers/cleanup_wrapper.py
    
.PARAMETER DryRun
    Preview changes without applying them
    
.PARAMETER OutputFormat
    Output format: text (default), json, yaml
    
.EXAMPLE
    .\cortex-cleanup.ps1
    Run cleanup with default settings
    
.EXAMPLE
    .\cortex-cleanup.ps1 -DryRun
    Preview cleanup actions without applying
    
.EXAMPLE
    .\cortex-cleanup.ps1 -OutputFormat json
    Get cleanup results in JSON format

.NOTES
    Author: Asif Hussain
    Copyright © 2025 Asif Hussain. All rights reserved.
    Version: 1.1.0 (Added old manifest cleanup)
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [ValidateSet('text', 'json', 'yaml')]
    [string]$OutputFormat = 'text'
)

# Get script directory (CORTEX root)
$CortexRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "🧹 CORTEX Cleanup" -ForegroundColor Cyan
Write-Host ""

# ========================================
# Step 1: Remove old manifest files
# ========================================
Write-Host "📂 Step 1: Scanning for old manifest files..." -ForegroundColor Yellow

$manifestsPath = Join-Path $CortexRoot "cortex-brain\manifests\orchestrators"
$oldManifests = @()

if (Test-Path $manifestsPath) {
    # Find all planning-system-*.yaml files
    $manifestFiles = Get-ChildItem -Path $manifestsPath -Filter "planning-system-*.yaml" -File
    
    foreach ($file in $manifestFiles) {
        # Read first 50 lines to find version
        $content = Get-Content $file.FullName -TotalCount 50 | Out-String
        
        # Extract version (format: version: "X.Y.Z" or version: "X.Y")
        if ($content -match 'version:\s*["'']?(\d+\.\d+(?:\.\d+)?)["'']?') {
            $version = $matches[1]
            $versionNum = [version]$version
            
            # Check if version < 4.0
            if ($versionNum -lt [version]"4.0") {
                $oldManifests += [PSCustomObject]@{
                    File = $file.FullName
                    RelativePath = $file.FullName.Replace($CortexRoot + "\", "")
                    Version = $version
                }
            }
        }
    }
    
    if ($oldManifests.Count -gt 0) {
        Write-Host "  Found $($oldManifests.Count) old manifest(s):" -ForegroundColor Red
        foreach ($manifest in $oldManifests) {
            Write-Host "    - $($manifest.RelativePath) (version $($manifest.Version))" -ForegroundColor Red
        }
        
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete these files" -ForegroundColor Gray
        } else {
            Write-Host "  Deleting old manifests..." -ForegroundColor Yellow
            foreach ($manifest in $oldManifests) {
                Remove-Item $manifest.File -Force
                Write-Host "    ✅ Deleted: $($manifest.RelativePath)" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "  ✅ No old manifests found (all are version 4.0+)" -ForegroundColor Green
    }
} else {
    Write-Host "  ⚠️  Manifests directory not found: $manifestsPath" -ForegroundColor Yellow
}

Write-Host ""

# ========================================
# Step 2: Run standard cleanup
# ========================================
Write-Host "📂 Step 2: Running standard cleanup..." -ForegroundColor Yellow

# Build command
$cmd = "python"
$args = @(
    "scripts/cli_wrappers/cleanup_wrapper.py",
    "--output", $OutputFormat
)

if ($DryRun) {
    $args += "--dry-run"
}

# Execute standard cleanup
Write-Host "Running: $cmd $($args -join ' ')" -ForegroundColor Gray
Write-Host ""

& $cmd @args

# Exit with same code
exit $LASTEXITCODE
