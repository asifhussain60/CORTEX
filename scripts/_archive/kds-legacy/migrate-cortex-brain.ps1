# CORTEX Brain Migration - Complete 3-Tier Data Migration
# Orchestrates migration of all CORTEX Brain data to SQLite

<#
.SYNOPSIS
    Migrates all CORTEX Brain data (Tiers 1-3) to SQLite database

.DESCRIPTION
    This script orchestrates the complete migration of CORTEX Brain data:
    - Tier 1: Conversation history (JSONL → SQLite)
    - Tier 2: Knowledge graph patterns (YAML → SQLite)
    - Tier 3: Development context metrics (YAML → SQLite)

.PARAMETER DbPath
    Path to SQLite database file (default: cortex-brain/cortex-brain.db)

.PARAMETER SourceDir
    Path to cortex-brain source directory (default: cortex-brain)

.PARAMETER SkipBackup
    Skip creating backup of existing database

.PARAMETER TierOnly
    Migrate only a specific tier (1, 2, or 3)

.EXAMPLE
    .\migrate-cortex-brain.ps1
    Migrates all tiers with default paths

.EXAMPLE
    .\migrate-cortex-brain.ps1 -TierOnly 1
    Migrates only Tier 1 (conversations)

.EXAMPLE
    .\migrate-cortex-brain.ps1 -SkipBackup
    Migrates all tiers without creating backup
#>

param(
    [string]$DbPath = "cortex-brain/cortex-brain.db",
    [string]$SourceDir = "cortex-brain",
    [switch]$SkipBackup,
    [ValidateSet(1, 2, 3, "all")]
    [string]$TierOnly = "all"
)

$ErrorActionPreference = "Stop"

# Get project root (script is in CORTEX/scripts/)
$ProjectRoot = Split-Path $PSScriptRoot -Parent

Write-Host "🧠 CORTEX Brain Migration Orchestrator" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Check required Python packages
Write-Host "Checking dependencies..." -ForegroundColor Yellow

$requiredPackages = @("pyyaml")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    $null = python -c "import $package" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host "⚠️  Missing Python packages: $($missingPackages -join ', ')" -ForegroundColor Yellow
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    
    foreach ($package in $missingPackages) {
        Write-Host "  Installing $package..." -ForegroundColor Gray
        python -m pip install $package --quiet
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install $package" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ All dependencies available" -ForegroundColor Green
}

Write-Host ""

# Resolve paths
$dbFullPath = Join-Path $ProjectRoot $DbPath
$sourceFullPath = Join-Path $ProjectRoot $SourceDir

# Determine which migration to run
if ($TierOnly -eq "all") {
    # Run complete migration
    Write-Host "Running complete migration (all tiers)..." -ForegroundColor Cyan
    Write-Host ""
    
    $scriptPath = Join-Path $PSScriptRoot "migrate-all-tiers.py"
    
    $migrationArgs = @(
        $scriptPath,
        "--db-path", $dbFullPath,
        "--source-dir", $sourceFullPath
    )
    
    if ($SkipBackup) {
        $migrationArgs += "--skip-backup"
    }
    
    python @migrationArgs
    
} else {
    # Run single tier migration
    Write-Host "Running Tier $TierOnly migration only..." -ForegroundColor Cyan
    Write-Host ""
    
    # First ensure schema exists
    $schemaScript = Join-Path $ProjectRoot "cortex-brain/migrate_brain_db.py"
    if (Test-Path $schemaScript) {
        Write-Host "Ensuring database schema exists..." -ForegroundColor Yellow
        python $schemaScript --db-path $dbFullPath
        Write-Host ""
    }
    
    # Run tier-specific migration
    $scriptName = switch ($TierOnly) {
        1 { "migrate-tier1-to-sqlite.py" }
        2 { "migrate-tier2-to-sqlite.py" }
        3 { "migrate-tier3-to-sqlite.py" }
    }
    
    $scriptPath = Join-Path $PSScriptRoot $scriptName
    
    python $scriptPath --db-path $dbFullPath --source-dir $sourceFullPath
}

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Migration completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Migration failed with exit code $exitCode" -ForegroundColor Red
}

exit $exitCode
