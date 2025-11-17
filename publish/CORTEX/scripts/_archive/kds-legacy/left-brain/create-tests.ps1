# TDD RED Phase: Create Tests Script
# Purpose: Automate test creation before implementation
# Phase: RED (tests should fail initially)

param(
    [Parameter(Mandatory=$true)]
    [string]$FeatureConfig,
    
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$workspaceRoot = "D:\PROJECTS\KDS"

# Load feature configuration
if (-not (Test-Path $FeatureConfig)) {
    throw "Feature config not found: $FeatureConfig"
}

# Show output only if not in quiet mode
if (-not $DryRun -or $env:KDS_VERBOSE) {
    Write-Host "`n🔴 TDD RED Phase: Creating Tests" -ForegroundColor Red
    Write-Host "=" * 60 -ForegroundColor Red
    Write-Host "Config: $FeatureConfig" -ForegroundColor Gray
}

# Parse YAML config (simple parsing for test purposes)
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
    task_id = "test-creation"
    phase = "RED"
    status = "started"
    feature_name = $featureName
    tests_created = @()
    files_modified = @()
}

if ($env:KDS_VERBOSE) {
    Write-Host "`n📝 Creating tests for: $featureName" -ForegroundColor Cyan
}

# In DryRun mode, simulate test creation
if ($DryRun) {
    if ($env:KDS_VERBOSE) {
        Write-Host "  [DRY RUN] Would create test files" -ForegroundColor Yellow
        Write-Host "  [DRY RUN] Would log to execution-state.jsonl" -ForegroundColor Yellow
    }
    
    $executionState.status = "completed"
    $executionState.tests_created = @("SampleButtonTests.cs")
    
    return @{
        tests_created = $true
        logged_to_execution_state = $true
        phase = "RED"
        feature_name = $featureName
        dry_run = $true
    }
}

# Real execution: Create test files
try {
    # Extract test file path from config
    if ($configContent -match 'tests:\s*-\s*path:\s*"([^"]+)"') {
        $testFilePath = Join-Path $workspaceRoot $Matches[1]
        $testDir = Split-Path $testFilePath -Parent
        
        # Create directory if needed
        if (-not (Test-Path $testDir)) {
            New-Item -ItemType Directory -Path $testDir -Force | Out-Null
            if ($env:KDS_VERBOSE) {
                Write-Host "  ✅ Created test directory: $testDir" -ForegroundColor Green
            }
        }
        
        # Extract test content template
        if ($configContent -match 'content_template:\s*\|([^}]+)') {
            $testContent = $Matches[1].Trim()
            
            # Write test file
            Set-Content -Path $testFilePath -Value $testContent -Force
            $executionState.tests_created += $testFilePath
            
            if ($env:KDS_VERBOSE) {
                Write-Host "  ✅ Created test file: $testFilePath" -ForegroundColor Green
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
        Write-Host "`n🔴 RED Phase: Tests created (should fail initially)" -ForegroundColor Red
    }
    
    return @{
        tests_created = $true
        logged_to_execution_state = $true
        phase = "RED"
        feature_name = $featureName
        test_files = $executionState.tests_created
    }
    
} catch {
    $executionState.status = "failed"
    $executionState.error_message = $_.Exception.Message
    
    # Log failure
    $executionStateJson = $executionState | ConvertTo-Json -Compress
    Add-Content -Path $executionStateFile -Value $executionStateJson
    
    throw "RED phase failed: $($_.Exception.Message)"
}
