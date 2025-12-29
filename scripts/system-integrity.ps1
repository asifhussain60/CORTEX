# System Integrity Check - Quick Launcher
# Simple wrapper for easy invocation

param(
    [switch]$NoFix,
    [switch]$NoTests,
    [switch]$NoDocs,
    [switch]$NoLegacy,
    [switch]$NoOrganize,
    [switch]$Verbose
)

$scriptPath = Join-Path $PSScriptRoot "cli_wrappers\system_integrity_wrapper.py"

$args = @()

if ($NoFix) { $args += "--no-fix" }
if ($NoTests) { $args += "--no-tests" }
if ($NoDocs) { $args += "--no-docs" }
if ($NoLegacy) { $args += "--no-legacy" }
if ($NoOrganize) { $args += "--no-organize" }
if ($Verbose) { $args += "--verbose" }

Write-Host "Running CORTEX System Integrity Check..." -ForegroundColor Cyan
Write-Host ""

python $scriptPath @args

Write-Host ""
Write-Host "System integrity check complete!" -ForegroundColor Green
