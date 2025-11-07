# TDD GREEN Phase: Implement Code Script
# Purpose: Create minimal implementation to make tests pass
# Phase: GREEN (tests should pass after implementation)

param(
    [Parameter(Mandatory=$true)]
    [string]$FeatureConfig,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

if (-not $DryRun -or $env:KDS_VERBOSE) {
    Write-Host "`n🟢 TDD GREEN Phase: Implementing Code" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "Config: $FeatureConfig" -ForegroundColor Gray
}

# Load feature configuration
if (-not (Test-Path $FeatureConfig)) {
    throw "Feature config not found: $FeatureConfig"
}

$configContent = Get-Content $FeatureConfig -Raw
$featureName = if ($configContent -match 'feature_name:\s*"([^"]+)"') { $Matches[1] } else { "Unknown Feature" }

# Generate timestamp
$timestamp = Get-Date -Format "o"
$sessionId = if (Test-Path "$workspaceRoot\cortex-brain\right-hemisphere\active-plan.yaml") {
    $activePlan = Get-Content "$workspaceRoot\cortex-brain\right-hemisphere\active-plan.yaml" -Raw
    if ($activePlan -match 'session_id:\s*"([^"]+)"') { $Matches[1] } else { "unknown-session" }
} else {
    "unknown-session"
}

# Create execution state entry
$executionState = @{
    timestamp = $timestamp
    session_id = $sessionId
    task_id = "code-implementation"
    phase = "GREEN"
    status = "started"
    feature_name = $featureName
    files_modified = @()
}

if ($env:KDS_VERBOSE) {
    Write-Host "`n📝 Implementing: $featureName" -ForegroundColor Cyan
}

# In DryRun mode, simulate implementation
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "  [DRY RUN] Would create implementation files" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would log to execution-state.jsonl" -ForegroundColor Yellow
    }
    
    $executionState.status = "completed"
    $executionState.files_modified = @("SampleButton.cs")
    
    return @{
        code_created = $true
        logged_to_execution_state = $true
        phase = "GREEN"
        feature_name = $featureName
        dry_run = $true
    }
}

# Real execution: Create implementation files
try {
    # Extract implementation file path from config
    if ($configContent -match 'implementation:\s*-\s*path:\s*"([^"]+)"') {
        $implFilePath = Join-Path $workspaceRoot $Matches[1]
        $implDir = Split-Path $implFilePath -Parent
        
        # Create directory if needed
        if (-not (Test-Path $implDir)) {
            New-Item -ItemType Directory -Path $implDir -Force | Out-Null
            if ($env:KDS_VERBOSE) {
                Write-Host "  ✅ Created implementation directory: $implDir" -ForegroundColor Green
            }
        }
        
        # Extract implementation content template
        $implStart = $configContent.IndexOf("implementation:")
        if ($implStart -ge 0 -and $configContent -match '(?s)content_template:\s*\|([^-]+)(?=\s+tests:)') {
            $implContent = $Matches[1].Trim()
            
            # Write implementation file
            Set-Content -Path $implFilePath -Value $implContent -Force
            $executionState.files_modified += $implFilePath
            
            if ($env:KDS_VERBOSE) {
                Write-Host "  ✅ Created implementation file: $implFilePath" -ForegroundColor Green
            }
        }
    }
    
    # Log to execution state
    $executionState.status = "completed"
    $executionStateFile = Join-Path $workspaceRoot "cortex-brain\left-hemisphere\execution-state.jsonl"
    
    $executionStateJson = $executionState | ConvertTo-Json -Compress
    Add-Content -Path $executionStateFile -Value $executionStateJson
    
    if ($env:KDS_VERBOSE) {
        Write-Host "  ✅ Logged to execution-state.jsonl" -ForegroundColor Green
        Write-Host "`n🟢 GREEN Phase: Implementation created (tests should pass now)" -ForegroundColor Green
    }
    
    return @{
        code_created = $true
        logged_to_execution_state = $true
        phase = "GREEN"
        feature_name = $featureName
        implementation_files = $executionState.files_modified
    }
    
} catch {
    $executionState.status = "failed"
    $executionState.error_message = $_.Exception.Message
    
    # Log failure
    $executionStateJson = $executionState | ConvertTo-Json -Compress
    Add-Content -Path $executionStateFile -Value $executionStateJson
    
    throw "GREEN phase failed: $($_.Exception.Message)"
}
