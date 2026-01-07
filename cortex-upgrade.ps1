# CORTEX Upgrade System - Windows PowerShell Script
# Version: 1.0.0 | Author: Asif Hussain | Date: January 6, 2026
# Purpose: Automated upgrade for CORTEX v5.0 on Windows machines

<#
.SYNOPSIS
    Upgrades CORTEX to the latest v5.0 enhancements from remote branch.

.DESCRIPTION
    This script performs a complete upgrade of the CORTEX system by:
    - Pulling latest changes from CORTEX-5.0 branch
    - Updating dependencies
    - Wiring new orchestrators
    - Rebuilding prompts and documentation
    - Setting up master/child orchestrator patterns
    - Integrating audit logging

.PARAMETER DryRun
    Analyze changes without making modifications

.PARAMETER AutoApprove
    Skip confirmation prompts (use with caution)

.PARAMETER SkipBackup
    Skip backup creation (not recommended)

.PARAMETER RollbackTo
    Rollback to a specific upgrade timestamp

.EXAMPLE
    .\cortex-upgrade.ps1
    Interactive upgrade with confirmations

.EXAMPLE
    .\cortex-upgrade.ps1 -DryRun
    Analyze without making changes

.EXAMPLE
    .\cortex-upgrade.ps1 -AutoApprove
    Automated upgrade (for CI/CD)

.EXAMPLE
    .\cortex-upgrade.ps1 -RollbackTo "20260106_143022"
    Rollback to specific backup

.NOTES
    Requires: PowerShell 5.1+, Python 3.11+, Git 2.30+
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$AutoApprove,
    [switch]$SkipBackup,
    [string]$RollbackTo = ""
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

$script:CORTEX_ROOT = $PSScriptRoot
$script:TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$script:UPGRADE_DIR = Join-Path $CORTEX_ROOT "cortex-brain\documents\upgrades\$TIMESTAMP"
$script:BACKUP_DIR = Join-Path $CORTEX_ROOT "backups\upgrade-$TIMESTAMP"
$script:LOG_FILE = Join-Path $UPGRADE_DIR "upgrade.log"

# Color codes for output
$script:COLOR_SUCCESS = "Green"
$script:COLOR_ERROR = "Red"
$script:COLOR_WARNING = "Yellow"
$script:COLOR_INFO = "Cyan"
$script:COLOR_HEADER = "Magenta"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n$('=' * 80)" -ForegroundColor $COLOR_HEADER
    Write-Host $Message -ForegroundColor $COLOR_HEADER
    Write-Host "$('=' * 80)`n" -ForegroundColor $COLOR_HEADER
}

function Write-Phase {
    param([string]$PhaseId, [string]$PhaseName)
    Write-Host "`n[PHASE $PhaseId]" -ForegroundColor $COLOR_INFO -NoNewline
    Write-Host " $PhaseName" -ForegroundColor White
    Write-Host "$('-' * 80)" -ForegroundColor $COLOR_INFO
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $COLOR_SUCCESS
}

function Write-Error-Message {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $COLOR_ERROR
}

function Write-Warning-Message {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $COLOR_WARNING
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $COLOR_INFO
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # Create log directory if it doesn't exist
    $logDir = Split-Path -Parent $LOG_FILE
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $LOG_FILE -Value $logEntry
}

function Invoke-Command-Safe {
    param(
        [string]$Command,
        [string]$Description,
        [bool]$CriticalFailure = $true
    )
    
    Write-Info $Description
    Write-Log "Executing: $Command" "DEBUG"
    
    try {
        $output = Invoke-Expression $Command 2>&1
        Write-Log $output "DEBUG"
        return $output
    }
    catch {
        $errorMsg = $_.Exception.Message
        Write-Error-Message $errorMsg
        Write-Log $errorMsg "ERROR"
        
        if ($CriticalFailure) {
            throw "Critical failure: $Description failed"
        }
        return $null
    }
}

function Get-UserConfirmation {
    param([string]$Message, [string]$DefaultChoice = "N")
    
    if ($AutoApprove) {
        Write-Info "Auto-approved: $Message"
        return $true
    }
    
    $choices = @(
        New-Object System.Management.Automation.Host.ChoiceDescription "&Yes", "Proceed with the action"
        New-Object System.Management.Automation.Host.ChoiceDescription "&No", "Cancel the action"
    )
    
    $defaultIndex = if ($DefaultChoice -eq "Y") { 0 } else { 1 }
    $decision = $Host.UI.PromptForChoice("Confirmation", $Message, $choices, $defaultIndex)
    
    return $decision -eq 0
}

# =============================================================================
# PRE-FLIGHT VALIDATION (Phase P01)
# =============================================================================

function Test-PreFlightChecks {
    Write-Phase "P01" "Pre-Flight Validation"
    
    $checks = @()
    
    # Check 1: Git working directory clean
    Write-Info "Checking git working directory..."
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Warning-Message "Working directory has uncommitted changes:"
        Write-Host $gitStatus
        $checks += @{ Name = "Git Status"; Passed = $false; Message = "Uncommitted changes detected" }
        
        if (-not (Get-UserConfirmation "Continue despite uncommitted changes?")) {
            throw "Aborted by user due to uncommitted changes"
        }
    }
    else {
        Write-Success "Working directory clean"
        $checks += @{ Name = "Git Status"; Passed = $true }
    }
    
    # Check 2: Current branch
    Write-Info "Checking current branch..."
    $currentBranch = git branch --show-current
    if ($currentBranch -ne "CORTEX-5.0") {
        Write-Warning-Message "Current branch: $currentBranch (expected: CORTEX-5.0)"
        $checks += @{ Name = "Git Branch"; Passed = $false; Message = "Not on CORTEX-5.0 branch" }
    }
    else {
        Write-Success "On CORTEX-5.0 branch"
        $checks += @{ Name = "Git Branch"; Passed = $true }
    }
    
    # Check 3: Python version
    Write-Info "Checking Python version..."
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(1[1-9]|[2-9][0-9])\.") {
        Write-Success "Python version: $pythonVersion"
        $checks += @{ Name = "Python Version"; Passed = $true }
    }
    else {
        Write-Error-Message "Python 3.11+ required (found: $pythonVersion)"
        $checks += @{ Name = "Python Version"; Passed = $false; Message = "Python 3.11+ required" }
        throw "Python version check failed"
    }
    
    # Check 4: Git version
    Write-Info "Checking Git version..."
    $gitVersion = git --version
    Write-Success "Git version: $gitVersion"
    $checks += @{ Name = "Git Version"; Passed = $true }
    
    # Check 5: Disk space
    Write-Info "Checking disk space..."
    $drive = (Get-Location).Drive
    $freeSpace = (Get-PSDrive $drive.Name).Free / 1MB
    if ($freeSpace -lt 500) {
        Write-Warning-Message "Low disk space: $([math]::Round($freeSpace, 2)) MB free"
        $checks += @{ Name = "Disk Space"; Passed = $false; Message = "Less than 500MB free" }
    }
    else {
        Write-Success "Disk space: $([math]::Round($freeSpace, 2)) MB free"
        $checks += @{ Name = "Disk Space"; Passed = $true }
    }
    
    # Check 6: Network connectivity
    Write-Info "Checking network connectivity..."
    try {
        git fetch --dry-run origin CORTEX-5.0 2>&1 | Out-Null
        Write-Success "Network connectivity OK"
        $checks += @{ Name = "Network"; Passed = $true }
    }
    catch {
        Write-Error-Message "Network connectivity failed"
        $checks += @{ Name = "Network"; Passed = $false; Message = "Cannot reach remote" }
        throw "Network connectivity check failed"
    }
    
    # Save pre-flight report
    $reportPath = Join-Path $UPGRADE_DIR "01-pre-flight-report.json"
    $checks | ConvertTo-Json -Depth 10 | Out-File $reportPath -Encoding UTF8
    Write-Info "Pre-flight report saved: $reportPath"
    
    $failedChecks = $checks | Where-Object { -not $_.Passed }
    if ($failedChecks.Count -gt 0 -and -not $AutoApprove) {
        Write-Warning-Message "$($failedChecks.Count) checks failed"
        if (-not (Get-UserConfirmation "Continue despite failed checks?")) {
            throw "Aborted by user due to failed checks"
        }
    }
    
    Write-Success "Pre-flight validation complete"
}

# =============================================================================
# REMOTE ANALYSIS (Phase P02)
# =============================================================================

function Get-RemoteAnalysis {
    Write-Phase "P02" "Remote Analysis"
    
    # Fetch latest from remote
    Write-Info "Fetching latest changes from origin/CORTEX-5.0..."
    git fetch origin CORTEX-5.0
    Write-Success "Fetch complete"
    
    # Get commit diff
    Write-Info "Analyzing commit differences..."
    $commitLog = git log HEAD..origin/CORTEX-5.0 --oneline
    $commitCount = ($commitLog | Measure-Object).Count
    
    if ($commitCount -eq 0) {
        Write-Success "Already up to date with remote"
        return @{ UpToDate = $true; CommitCount = 0 }
    }
    
    Write-Info "Found $commitCount new commits:"
    $commitLog | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    
    # Get file diff
    Write-Info "Analyzing file changes..."
    $fileDiff = git diff --stat HEAD..origin/CORTEX-5.0
    Write-Host $fileDiff -ForegroundColor Gray
    
    # Categorize changes by subsystem
    $changedFiles = git diff --name-only HEAD..origin/CORTEX-5.0
    $subsystems = @{
        orchestrators = @($changedFiles | Where-Object { $_ -like "src/orchestrators/*" })
        prompts = @($changedFiles | Where-Object { $_ -like ".github/prompts/*" })
        documentation = @($changedFiles | Where-Object { $_ -like "cortex-brain/documents/*" })
        audit_logging = @($changedFiles | Where-Object { $_ -like "src/logging/*" })
        architecture = @($changedFiles | Where-Object { $_ -like "src/core/*" -or $_ -like "src/entry_point/*" })
        tests = @($changedFiles | Where-Object { $_ -like "tests/*" })
    }
    
    Write-Info "Changes by subsystem:"
    foreach ($key in $subsystems.Keys) {
        $count = $subsystems[$key].Count
        if ($count -gt 0) {
            Write-Host "  $key : $count files" -ForegroundColor Cyan
        }
    }
    
    # Save analysis
    $analysis = @{
        UpToDate = $false
        CommitCount = $commitCount
        Commits = $commitLog
        FilesChanged = $changedFiles.Count
        Subsystems = $subsystems
        Timestamp = (Get-Date).ToString("o")
    }
    
    $analysisPath = Join-Path $UPGRADE_DIR "02-remote-analysis.json"
    $analysis | ConvertTo-Json -Depth 10 | Out-File $analysisPath -Encoding UTF8
    
    # Save diff summary
    $diffPath = Join-Path $UPGRADE_DIR "03-diff-summary.md"
    @"
# Remote Analysis - $TIMESTAMP

## Summary
- **Commits:** $commitCount
- **Files Changed:** $($changedFiles.Count)

## Commits
``````
$commitLog
``````

## File Changes
``````
$fileDiff
``````

## Subsystems Affected
$(foreach ($key in $subsystems.Keys) {
    $count = $subsystems[$key].Count
    if ($count -gt 0) {
        "- **$key**: $count files"
    }
})
"@ | Out-File $diffPath -Encoding UTF8
    
    Write-Success "Remote analysis complete"
    return $analysis
}

# =============================================================================
# BACKUP & ROLLBACK PREPARATION (Phase P03)
# =============================================================================

function New-Backup {
    Write-Phase "P03" "Backup & Rollback Preparation"
    
    if ($SkipBackup) {
        Write-Warning-Message "Skipping backup (not recommended)"
        return
    }
    
    Write-Info "Creating backup directory: $BACKUP_DIR"
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
    
    # Backup critical files
    $backupTargets = @(
        @{ Source = "cortex.config.json"; Destination = "cortex.config.json" }
        @{ Source = ".github\prompts\CORTEX.prompt.md"; Destination = "CORTEX.prompt.md" }
        @{ Source = ".github\copilot-instructions.md"; Destination = "copilot-instructions.md" }
        @{ Source = "cortex-brain\config\master-orchestrator.yaml"; Destination = "master-orchestrator.yaml" }
    )
    
    foreach ($target in $backupTargets) {
        $sourcePath = Join-Path $CORTEX_ROOT $target.Source
        $destPath = Join-Path $BACKUP_DIR $target.Destination
        
        if (Test-Path $sourcePath) {
            Write-Info "Backing up: $($target.Source)"
            Copy-Item -Path $sourcePath -Destination $destPath -Force
        }
    }
    
    # Backup active plans
    $activePlansSource = Join-Path $CORTEX_ROOT "cortex-brain\documents\planning\active"
    $activePlansDest = Join-Path $BACKUP_DIR "active-plans"
    
    if (Test-Path $activePlansSource) {
        Write-Info "Backing up active plans..."
        Copy-Item -Path $activePlansSource -Destination $activePlansDest -Recurse -Force
    }
    
    # Record current state
    $currentCommit = git rev-parse HEAD
    $currentBranch = git branch --show-current
    
    $manifest = @{
        Timestamp = $TIMESTAMP
        CommitSHA = $currentCommit
        Branch = $currentBranch
        PythonVersion = (python --version 2>&1)
        FilesBackedUp = ($backupTargets.Count + 1)  # +1 for active plans
        BackupDirectory = $BACKUP_DIR
    }
    
    $manifestPath = Join-Path $BACKUP_DIR "manifest.json"
    $manifest | ConvertTo-Json -Depth 10 | Out-File $manifestPath -Encoding UTF8
    
    # Create rollback script
    $rollbackScript = @"
# CORTEX Rollback Script - Generated $TIMESTAMP
# Restores system to state before upgrade

`$ErrorActionPreference = "Stop"

Write-Host "Starting rollback to commit $currentCommit..." -ForegroundColor Yellow

# Reset git
Write-Host "Resetting git to $currentCommit..."
git reset --hard $currentCommit

# Restore config files
Write-Host "Restoring backed up files..."
Copy-Item -Path "$BACKUP_DIR\cortex.config.json" -Destination "$CORTEX_ROOT\cortex.config.json" -Force
Copy-Item -Path "$BACKUP_DIR\CORTEX.prompt.md" -Destination "$CORTEX_ROOT\.github\prompts\CORTEX.prompt.md" -Force
Copy-Item -Path "$BACKUP_DIR\copilot-instructions.md" -Destination "$CORTEX_ROOT\.github\copilot-instructions.md" -Force
Copy-Item -Path "$BACKUP_DIR\master-orchestrator.yaml" -Destination "$CORTEX_ROOT\cortex-brain\config\master-orchestrator.yaml" -Force

# Restore active plans
Write-Host "Restoring active plans..."
Remove-Item -Path "$CORTEX_ROOT\cortex-brain\documents\planning\active\*" -Recurse -Force
Copy-Item -Path "$BACKUP_DIR\active-plans\*" -Destination "$CORTEX_ROOT\cortex-brain\documents\planning\active\" -Recurse -Force

# Verify
Write-Host "Verifying rollback..."
python -m src.main "help" --format markdown

Write-Host "Rollback complete!" -ForegroundColor Green
"@
    
    $rollbackPath = Join-Path $BACKUP_DIR "rollback.ps1"
    $rollbackScript | Out-File $rollbackPath -Encoding UTF8
    
    Write-Success "Backup complete: $BACKUP_DIR"
    Write-Info "Rollback script: $rollbackPath"
}

# =============================================================================
# GIT PULL & MERGE (Phase P04)
# =============================================================================

function Invoke-GitPull {
    param([object]$RemoteAnalysis)
    
    Write-Phase "P04" "Git Pull & Merge"
    
    if ($RemoteAnalysis.UpToDate) {
        Write-Success "Already up to date - skipping git pull"
        return
    }
    
    $commitCount = $RemoteAnalysis.CommitCount
    if (-not (Get-UserConfirmation "Ready to pull $commitCount commits. Proceed?")) {
        throw "Aborted by user"
    }
    
    Write-Info "Pulling with rebase strategy..."
    try {
        $pullOutput = git pull --rebase origin CORTEX-5.0 2>&1
        
        # Save pull log
        $pullLogPath = Join-Path $UPGRADE_DIR "04-git-pull-log.txt"
        $pullOutput | Out-File $pullLogPath -Encoding UTF8
        
        Write-Success "Git pull complete"
    }
    catch {
        Write-Error-Message "Git pull failed: $_"
        
        # Check for conflicts
        $conflicts = git diff --name-only --diff-filter=U
        if ($conflicts) {
            Write-Warning-Message "Merge conflicts detected in:"
            $conflicts | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
            
            $conflictsPath = Join-Path $UPGRADE_DIR "05-conflicts.json"
            @{ Conflicts = $conflicts; Timestamp = (Get-Date).ToString("o") } | 
                ConvertTo-Json | Out-File $conflictsPath -Encoding UTF8
            
            if (Get-UserConfirmation "Resolve conflicts manually now?") {
                Write-Info "Please resolve conflicts and run: git rebase --continue"
                Write-Info "Then re-run this script to continue upgrade"
                exit 1
            }
            else {
                Write-Info "Rolling back..."
                git rebase --abort
                throw "Aborted due to merge conflicts"
            }
        }
        
        throw
    }
}

# =============================================================================
# DEPENDENCY SYNCHRONIZATION (Phase P05)
# =============================================================================

function Update-Dependencies {
    Write-Phase "P05" "Dependency Synchronization"
    
    Write-Info "Installing updated dependencies..."
    $pipOutput = python -m pip install -r requirements.txt --upgrade 2>&1
    
    # Save pip log
    $pipLogPath = Join-Path $UPGRADE_DIR "07-pip-install-log.txt"
    $pipOutput | Out-File $pipLogPath -Encoding UTF8
    
    # Verify critical packages
    Write-Info "Verifying critical packages..."
    $criticalPackages = @("pytest", "pydantic", "PyYAML", "Jinja2", "watchdog", "requests")
    
    foreach ($pkg in $criticalPackages) {
        try {
            $testImport = "import $($pkg.ToLower().Replace('-', '_'))"
            python -c $testImport 2>&1 | Out-Null
            Write-Success "$pkg installed"
        }
        catch {
            Write-Error-Message "$pkg verification failed"
            throw "Critical package missing: $pkg"
        }
    }
    
    # Test audit logger import
    Write-Info "Testing audit logger import..."
    python -c "from src.logging.audit_logger import AuditLogger" 2>&1 | Out-Null
    Write-Success "Audit logger import successful"
    
    Write-Success "Dependencies synchronized"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Start-Upgrade {
    try {
        Write-Header "🚀 CORTEX v5.0 Upgrade System - Windows PowerShell"
        Write-Host "Timestamp: $TIMESTAMP" -ForegroundColor Gray
        Write-Host "Cortex Root: $CORTEX_ROOT" -ForegroundColor Gray
        
        if ($DryRun) {
            Write-Warning-Message "DRY RUN MODE - No changes will be made"
        }
        
        # Create upgrade directory
        New-Item -ItemType Directory -Path $UPGRADE_DIR -Force | Out-Null
        Write-Info "Upgrade directory: $UPGRADE_DIR"
        
        Write-Log "Upgrade started" "INFO"
        
        # Phase P01: Pre-Flight Validation
        Test-PreFlightChecks
        
        # Phase P02: Remote Analysis
        $remoteAnalysis = Get-RemoteAnalysis
        
        if ($remoteAnalysis.UpToDate) {
            Write-Success "System is already up to date!"
            Write-Info "No upgrade needed."
            exit 0
        }
        
        if ($DryRun) {
            Write-Info "Dry run complete - no changes made"
            Write-Info "Review analysis: $UPGRADE_DIR"
            exit 0
        }
        
        # Phase P03: Backup & Rollback Preparation
        New-Backup
        
        # Phase P04: Git Pull & Merge
        Invoke-GitPull -RemoteAnalysis $remoteAnalysis
        
        # Phase P05: Dependency Synchronization
        Update-Dependencies
        
        # Phase P06-P12: Invoke Python orchestrator for remaining phases
        Write-Header "🛡️ Invoking Python Orchestrator for Advanced Phases"
        Write-Info "Phases P06-P12 will be executed by Python orchestrator..."
        
        $pythonCommand = "python -m src.main `"upgrade cortex phases 06-12`" --format markdown"
        Write-Info "Command: $pythonCommand"
        
        Invoke-Expression $pythonCommand
        
        Write-Header "🎉 CORTEX Upgrade Complete!"
        Write-Success "All phases executed successfully"
        Write-Info "Upgrade documentation: $UPGRADE_DIR"
        Write-Info "Backup location: $BACKUP_DIR"
        Write-Info "Executive summary: $UPGRADE_DIR\EXECUTIVE-SUMMARY.md"
        
        Write-Log "Upgrade completed successfully" "INFO"
        
    }
    catch {
        Write-Header "❌ UPGRADE FAILED"
        Write-Error-Message $_.Exception.Message
        Write-Log $_.Exception.Message "ERROR"
        
        Write-Info "Rollback script available: $BACKUP_DIR\rollback.ps1"
        Write-Info "To rollback: .\$BACKUP_DIR\rollback.ps1"
        
        exit 1
    }
}

# =============================================================================
# ROLLBACK EXECUTION
# =============================================================================

function Start-Rollback {
    param([string]$Timestamp)
    
    Write-Header "🔄 CORTEX Rollback System"
    
    $rollbackDir = Join-Path $CORTEX_ROOT "backups\upgrade-$Timestamp"
    
    if (-not (Test-Path $rollbackDir)) {
        Write-Error-Message "Backup not found: $rollbackDir"
        exit 1
    }
    
    $rollbackScript = Join-Path $rollbackDir "rollback.ps1"
    
    if (-not (Test-Path $rollbackScript)) {
        Write-Error-Message "Rollback script not found: $rollbackScript"
        exit 1
    }
    
    if (Get-UserConfirmation "Execute rollback to $Timestamp?") {
        & $rollbackScript
    }
    else {
        Write-Info "Rollback cancelled"
    }
}

# =============================================================================
# ENTRY POINT
# =============================================================================

if ($RollbackTo) {
    Start-Rollback -Timestamp $RollbackTo
}
else {
    Start-Upgrade
}
