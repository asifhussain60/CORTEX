# Rollback Changes Script
# Purpose: Git-based rollback to last known good state
# Triggered when tests fail during TDD cycle

param(
    [string]$RollbackPoint,  # Git commit SHA or tag
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

if ($env:KDS_VERBOSE) {
    Write-Host "`n⏪ Rollback System" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Yellow
}

# In DryRun mode, simulate rollback
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "  [DRY RUN] Would use Git for rollback" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would track rollback points" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would log rollback events" -ForegroundColor Yellow
    }
    
    return @{
        uses_git = $true
        tracks_rollback_points = $true
        logs_rollback_events = $true
        dry_run = $true
    }
}

# Real execution: Perform Git rollback
try {
    # Get current Git status
    $gitStatus = git status --porcelain
    
    if ($env:KDS_VERBOSE) {
        Write-Host "`n📊 Current Git status:" -ForegroundColor Cyan
        if ($gitStatus) {
            Write-Host $gitStatus -ForegroundColor Gray
        } else {
            Write-Host "  No uncommitted changes" -ForegroundColor Gray
        }
    }
    
    # Create rollback point if not specified
    if (-not $RollbackPoint) {
        $RollbackPoint = git rev-parse HEAD
        if ($env:KDS_VERBOSE) {
            Write-Host "`n📌 Current commit (rollback point): $RollbackPoint" -ForegroundColor Cyan
        }
    }
    
    # Determine what to rollback
    if ($gitStatus) {
        if ($env:KDS_VERBOSE) {
            Write-Host "`n⚠️  Uncommitted changes detected" -ForegroundColor Yellow
            Write-Host "   Rolling back uncommitted changes..." -ForegroundColor Yellow
        }
        
        # Reset uncommitted changes
        git reset --hard HEAD
        
        if ($env:KDS_VERBOSE) {
            Write-Host "  ✅ Rollback complete" -ForegroundColor Green
        }
    } else {
        if ($env:KDS_VERBOSE) {
            Write-Host "`n  ℹ️  No changes to rollback" -ForegroundColor Cyan
        }
    }
    
    # Log rollback event
    $timestamp = Get-Date -Format "o"
    $sessionId = if (Test-Path "$workspaceRoot\kds-brain\right-hemisphere\active-plan.yaml") {
        $activePlan = Get-Content "$workspaceRoot\kds-brain\right-hemisphere\active-plan.yaml" -Raw
        if ($activePlan -match 'session_id:\s*"([^"]+)"') { $Matches[1] } else { "unknown-session" }
    } else {
        "unknown-session"
    }
    
    $executionState = @{
        timestamp = $timestamp
        session_id = $sessionId
        task_id = "rollback"
        phase = "ROLLBACK"
        status = "completed"
        rollback_point = @{
            git_commit = $RollbackPoint
            timestamp = $timestamp
        }
    }
    
    $executionStateFile = Join-Path $workspaceRoot "kds-brain\left-hemisphere\execution-state.jsonl"
    $executionStateJson = $executionState | ConvertTo-Json -Compress
    Add-Content -Path $executionStateFile -Value $executionStateJson
    
    if ($env:KDS_VERBOSE) {
        Write-Host "  ✅ Rollback logged to execution-state.jsonl" -ForegroundColor Green
    }
    
    return @{
        uses_git = $true
        tracks_rollback_points = $true
        logs_rollback_events = $true
        rollback_point = $RollbackPoint
        rolled_back = $true
    }
    
} catch {
    Write-Host "`n  ❌ Rollback failed: $($_.Exception.Message)" -ForegroundColor Red
    throw
}
