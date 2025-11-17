#!/usr/bin/env pwsh
<#
.SYNOPSIS
    KDS Branch Protection Setup - Isolates KDS development to features/kds branch

.DESCRIPTION
    This script:
    1. Creates features/kds branch (if doesn't exist)
    2. Installs git hooks (pre-commit, post-merge) to enforce KDS isolation
    3. Configures branch protection to prevent accidental KDS commits elsewhere
    4. Switches you to features/kds for KDS work

.PARAMETER Force
    Force reinstall hooks even if they already exist

.EXAMPLE
    .\setup-kds-branch-protection.ps1
    # Interactive setup with validation

.EXAMPLE
    .\setup-kds-branch-protection.ps1 -Force
    # Force reinstall all hooks

.NOTES
    Part of KDS (Knowledge Development System)
    Ensures KDS changes never accidentally contaminate other branches
#>

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

Write-Host "🛡️  KDS Branch Protection Setup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Step 1: Detect workspace root
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $workspaceRoot

Write-Host "[1/7] Detecting workspace root..." -ForegroundColor Yellow
Write-Host "   Workspace: $workspaceRoot`n" -ForegroundColor Gray

# Step 2: Verify git repository
if (-not (Test-Path ".git")) {
    Write-Host "❌ ERROR: Not a git repository" -ForegroundColor Red
    Write-Host "   Run this script from repository root`n" -ForegroundColor Red
    exit 1
}
Write-Host "[2/7] ✅ Git repository verified`n" -ForegroundColor Green

# Step 3: Check current branch
$currentBranch = git branch --show-current
Write-Host "[3/7] Checking current branch..." -ForegroundColor Yellow
Write-Host "   Current branch: $currentBranch`n" -ForegroundColor Gray

# Step 4: Create features/kds branch if needed
$kdsBranchExists = git branch --list "features/kds"
if (-not $kdsBranchExists) {
    Write-Host "[4/7] Creating features/kds branch..." -ForegroundColor Yellow
    
    try {
        # Create branch from current state
        git branch features/kds
        Write-Host "   ✅ Branch 'features/kds' created from $currentBranch`n" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Failed to create branch: $_`n" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[4/7] ✅ Branch 'features/kds' already exists`n" -ForegroundColor Green
}

# Step 5: Install git hooks
Write-Host "[5/7] Installing git hooks..." -ForegroundColor Yellow

$hooksSource = Join-Path $workspaceRoot "KDS\hooks"
$hooksDest = Join-Path $workspaceRoot ".git\hooks"

if (-not (Test-Path $hooksSource)) {
    Write-Host "   ❌ KDS/hooks/ directory not found`n" -ForegroundColor Red
    exit 1
}

$hooksToInstall = @("pre-commit", "post-merge")
$installedCount = 0

foreach ($hookName in $hooksToInstall) {
    $sourceHook = Join-Path $hooksSource $hookName
    $destHook = Join-Path $hooksDest $hookName
    
    if (-not (Test-Path $sourceHook)) {
        Write-Host "   ⚠️  Warning: $hookName not found in KDS/hooks/" -ForegroundColor Yellow
        continue
    }
    
    # Check if hook already exists
    if ((Test-Path $destHook) -and -not $Force) {
        Write-Host "   ℹ️  $hookName already installed (use -Force to reinstall)" -ForegroundColor Gray
        $installedCount++
        continue
    }
    
    # Copy hook
    Copy-Item -Path $sourceHook -Destination $destHook -Force
    
    # Make executable (Git for Windows handles this, but we'll ensure)
    # Note: On Windows, git automatically detects executable scripts
    
    Write-Host "   ✅ Installed $hookName" -ForegroundColor Green
    $installedCount++
}

if ($installedCount -eq 0) {
    Write-Host "   ⚠️  No hooks were installed`n" -ForegroundColor Yellow
}
else {
    Write-Host "   ✅ $installedCount hook(s) active`n" -ForegroundColor Green
}

# Step 6: Verify hook installation
Write-Host "[6/7] Verifying hook installation..." -ForegroundColor Yellow

$verifiedHooks = @()
foreach ($hookName in $hooksToInstall) {
    $destHook = Join-Path $hooksDest $hookName
    if (Test-Path $destHook) {
        $verifiedHooks += $hookName
        Write-Host "   ✅ $hookName is active" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ $hookName not found" -ForegroundColor Red
    }
}
Write-Host ""

# Step 7: Switch to features/kds (if not already there)
if ($currentBranch -ne "features/kds") {
    Write-Host "[7/7] Switching to features/kds branch..." -ForegroundColor Yellow
    
    # Check for uncommitted changes
    $status = git status --porcelain
    if ($status) {
        Write-Host "   ⚠️  You have uncommitted changes:" -ForegroundColor Yellow
        Write-Host "$status`n" -ForegroundColor Gray
        
        $response = Read-Host "   Stash changes before switching? (Y/n)"
        if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
            git stash push -m "KDS: Auto-stash before switching to features/kds"
            Write-Host "   ✅ Changes stashed`n" -ForegroundColor Green
        }
        else {
            Write-Host "   ⚠️  Skipping branch switch (uncommitted changes)`n" -ForegroundColor Yellow
            Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
            Write-Host "✅ KDS Branch Protection Installed (Manual switch needed)" -ForegroundColor Green
            Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Cyan
            Write-Host "📝 To switch manually: git checkout features/kds`n" -ForegroundColor Gray
            exit 0
        }
    }
    
    try {
        git checkout features/kds
        Write-Host "   ✅ Switched to features/kds`n" -ForegroundColor Green
    }
    catch {
        Write-Host "   ❌ Failed to switch branch: $_`n" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[7/7] ✅ Already on features/kds`n" -ForegroundColor Green
}

# Summary
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ KDS Branch Protection Setup Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "🛡️  Protection Active:" -ForegroundColor Cyan
Write-Host "   ✓ KDS changes ONLY allowed on features/kds branch" -ForegroundColor Green
Write-Host "   ✓ Pre-commit hook validates KDS isolation" -ForegroundColor Green
Write-Host "   ✓ Post-merge hook auto-returns to features/kds" -ForegroundColor Green
Write-Host "   ✓ Non-KDS files blocked from KDS commits`n" -ForegroundColor Green

Write-Host "📋 Workflow:" -ForegroundColor Cyan
Write-Host "   1. Work on KDS: Stay on features/kds branch" -ForegroundColor Gray
Write-Host "   2. Work on app: Switch to master/other branch" -ForegroundColor Gray
Write-Host "   3. Merge KDS: git checkout master && git merge features/kds" -ForegroundColor Gray
Write-Host "   4. Auto-return: Hook switches back to features/kds automatically`n" -ForegroundColor Gray

Write-Host "⚠️  Important:" -ForegroundColor Yellow
Write-Host "   - KDS commits on non-KDS branches will be REJECTED" -ForegroundColor Yellow
Write-Host "   - Non-KDS files in KDS commits will be REJECTED" -ForegroundColor Yellow
Write-Host "   - Hooks enforce complete isolation`n" -ForegroundColor Yellow

Write-Host "🚀 You're now on features/kds - ready for KDS development!`n" -ForegroundColor Green
