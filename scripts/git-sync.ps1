#!/usr/bin/env pwsh
<#
.SYNOPSIS
    CORTEX Git Sync - Safe cross-machine synchronization
    
.DESCRIPTION
    Ensures deleted files on one machine are properly removed when syncing to another.
    Uses hard reset to match remote branch exactly.
    
.PARAMETER Safe
    Use rebase instead of hard reset (preserves local changes)
    
.PARAMETER DryRun
    Show what would be done without making changes
    
.EXAMPLE
    .\git-sync.ps1
    Standard sync (hard reset to match remote)
    
.EXAMPLE
    .\git-sync.ps1 -Safe
    Safe sync (rebase local changes)
    
.EXAMPLE
    .\git-sync.ps1 -DryRun
    Preview changes without executing

.NOTES
    Author: Asif Hussain
    Copyright © 2025 Asif Hussain. All rights reserved.
#>

param(
    [switch]$Safe,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "`n" -NoNewline
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "  🔄 CORTEX Git Sync" -ForegroundColor Cyan
Write-Host "="*70 -ForegroundColor Cyan

# Get current branch
$currentBranch = git branch --show-current
Write-Host "`n📍 Current Branch: " -NoNewline
Write-Host $currentBranch -ForegroundColor Yellow

# Check for uncommitted changes
$status = git status --porcelain
if ($status -and -not $DryRun) {
    Write-Host "`n⚠️  Warning: You have uncommitted changes" -ForegroundColor Yellow
    Write-Host $status
    Write-Host "`nThese changes will be " -NoNewline
    if ($Safe) {
        Write-Host "preserved and rebased" -ForegroundColor Green
    } else {
        Write-Host "LOST with hard reset" -ForegroundColor Red
    }
    
    $response = Read-Host "`nContinue? (yes/no)"
    if ($response -ne "yes") {
        Write-Host "`n❌ Sync cancelled" -ForegroundColor Red
        exit 1
    }
}

if ($DryRun) {
    Write-Host "`n🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Magenta
}

# Fetch all changes
Write-Host "`n📡 Fetching from remote..." -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "   Would run: git fetch --all --prune" -ForegroundColor Gray
} else {
    git fetch --all --prune
    Write-Host "   ✅ Fetch complete" -ForegroundColor Green
}

# Show what will be deleted/changed
Write-Host "`n📊 Changes from remote:" -ForegroundColor Cyan
$diff = git diff --name-status "origin/$currentBranch"
if ($diff) {
    $diff | ForEach-Object {
        $parts = $_ -split '\s+', 2
        $status = $parts[0]
        $file = $parts[1]
        
        switch ($status) {
            "D" { Write-Host "   🗑️  DELETE: $file" -ForegroundColor Red }
            "A" { Write-Host "   ➕ ADD:    $file" -ForegroundColor Green }
            "M" { Write-Host "   📝 MODIFY: $file" -ForegroundColor Yellow }
            default { Write-Host "   $status $file" -ForegroundColor Gray }
        }
    }
} else {
    Write-Host "   ✅ Already up to date" -ForegroundColor Green
}

# Perform sync
Write-Host "`n🔄 Syncing..." -ForegroundColor Cyan
if ($DryRun) {
    if ($Safe) {
        Write-Host "   Would run: git pull --rebase origin $currentBranch" -ForegroundColor Gray
    } else {
        Write-Host "   Would run: git reset --hard origin/$currentBranch" -ForegroundColor Gray
    }
} else {
    if ($Safe) {
        Write-Host "   Using safe rebase mode..." -ForegroundColor Yellow
        git pull --rebase "origin" $currentBranch
    } else {
        Write-Host "   Using hard reset (exact match with remote)..." -ForegroundColor Yellow
        git reset --hard "origin/$currentBranch"
    }
    Write-Host "   ✅ Sync complete" -ForegroundColor Green
}

# Clean up untracked files from deleted directories
Write-Host "`n🧹 Checking for orphaned files..." -ForegroundColor Cyan
$untracked = git ls-files --others --exclude-standard
if ($untracked) {
    Write-Host "   Found untracked files:" -ForegroundColor Yellow
    $untracked | ForEach-Object { Write-Host "     - $_" -ForegroundColor Gray }
    
    if (-not $DryRun) {
        $response = Read-Host "`n   Remove untracked files? (yes/no)"
        if ($response -eq "yes") {
            git clean -fd
            Write-Host "   ✅ Untracked files removed" -ForegroundColor Green
        }
    } else {
        Write-Host "   Would prompt to remove with: git clean -fd" -ForegroundColor Gray
    }
} else {
    Write-Host "   ✅ No orphaned files" -ForegroundColor Green
}

# Final status
Write-Host "`n📊 Final Status:" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "   (DRY RUN - no changes made)" -ForegroundColor Magenta
} else {
    $finalStatus = git status --short
    if ($finalStatus) {
        git status --short
    } else {
        Write-Host "   ✅ Working tree clean" -ForegroundColor Green
    }
}

Write-Host "`n" -NoNewline
Write-Host "="*70 -ForegroundColor Cyan
Write-Host "  ✅ CORTEX Git Sync Complete" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Cyan
Write-Host ""
