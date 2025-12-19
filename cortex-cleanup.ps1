#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Quick CORTEX cleanup command
    
.DESCRIPTION
    Executes the CORTEX holistic cleanup orchestrator.
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
    Version: 1.0.0
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [ValidateSet('text', 'json', 'yaml')]
    [string]$OutputFormat = 'text'
)

# Get script directory (CORTEX root)
$CortexRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Build command
$cmd = "python"
$args = @(
    "scripts/cli_wrappers/cleanup_wrapper.py",
    "--output", $OutputFormat
)

if ($DryRun) {
    $args += "--dry-run"
}

# Execute
Write-Host "🧹 CORTEX Cleanup" -ForegroundColor Cyan
Write-Host "Running: $cmd $($args -join ' ')" -ForegroundColor Gray
Write-Host ""

& $cmd @args

# Exit with same code
exit $LASTEXITCODE
