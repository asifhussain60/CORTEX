<#
.SYNOPSIS
Test Tier 1 auto-recording system (all 3 layers)

.DESCRIPTION
Validates Layer 1 (Copilot Chat import), Layer 2 (Session recording),
and Layer 3 (Manual recording) of the Tier 1 tracking system.

.EXAMPLE
.\test-tier1-tracking.ps1
Run all Tier 1 tracking tests

.NOTES
Author: KDS v7.0
Created: 2025-11-05
Part of: Tier 1 Underutilization Fix
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🧪 Testing Tier 1 Auto-Recording System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Helper function for test results
function Test-Result {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Details = ""
    )
    
    if ($Passed) {
        Write-Host "  ✅ $TestName" -ForegroundColor Green
        if ($Details) {
            Write-Host "     $Details" -ForegroundColor Gray
        }
        $script:testsPassed++
    } else {
        Write-Host "  ❌ $TestName" -ForegroundColor Red
        if ($Details) {
            Write-Host "     $Details" -ForegroundColor Yellow
        }
        $script:testsFailed++
    }
}

# ========================================
# TEST LAYER 3: Manual Recording
# ========================================
Write-Host "📝 Layer 3: Manual Recording" -ForegroundColor Yellow
Write-Host ""

# Test 1: record-conversation.ps1 exists
$recordScriptPath = "scripts\record-conversation.ps1"
Test-Result -TestName "record-conversation.ps1 exists" `
    -Passed (Test-Path $recordScriptPath) `
    -Details "Path: $recordScriptPath"

# Test 2: conversation-history.jsonl exists
$conversationHistoryPath = "kds-brain\conversation-history.jsonl"
Test-Result -TestName "conversation-history.jsonl exists" `
    -Passed (Test-Path $conversationHistoryPath) `
    -Details "Path: $conversationHistoryPath"

# Test 3: Manual recording works
try {
    $testConvId = "test-manual-$(Get-Random -Maximum 9999)"
    & $recordScriptPath `
        -Title "Test Manual Recording $testConvId" `
        -FilesModified "test-file.ps1" `
        -EntitiesDiscussed "test-entity" `
        -Outcome "Test completed successfully" `
        -Intent "TEST" `
        -ErrorAction Stop | Out-Null
    
    # Verify entry was created
    $conversations = Get-Content $conversationHistoryPath | ForEach-Object { $_ | ConvertFrom-Json }
    $testConv = $conversations | Where-Object { $_.title -like "*$testConvId*" }
    
    Test-Result -TestName "Manual recording creates entry" `
        -Passed ($null -ne $testConv) `
        -Details "Conversation ID: $($testConv.conversation_id)"
    
} catch {
    Test-Result -TestName "Manual recording creates entry" `
        -Passed $false `
        -Details "Error: $_"
}

Write-Host ""

# ========================================
# TEST LAYER 2: Session Recording
# ========================================
Write-Host "📋 Layer 2: Session Recording" -ForegroundColor Yellow
Write-Host ""

# Test 1: record-session-conversation.ps1 exists
$sessionRecordPath = "scripts\record-session-conversation.ps1"
Test-Result -TestName "record-session-conversation.ps1 exists" `
    -Passed (Test-Path $sessionRecordPath) `
    -Details "Path: $sessionRecordPath"

# Test 2: Sessions directory exists
$sessionDir = "sessions"
Test-Result -TestName "Sessions directory exists" `
    -Passed (Test-Path $sessionDir) `
    -Details "Path: $sessionDir"

# Test 3: Session recording works
try {
    $testSessionId = "test-session-$(Get-Random -Maximum 9999)"
    $testSessionFile = "sessions\test-$testSessionId.json"
    
    # Create test session
    $testSession = @{
        session_id = $testSessionId
        title = "Test Session Recording"
        start_time = (Get-Date).AddHours(-1).ToString("o")
        end_time = (Get-Date).ToString("o")
        active = $false
        tasks = @("Task 1", "Task 2")
        outcome = "Test completed"
        intent = "TEST"
        entities = @("test-entity")
        files_modified = @("test.ps1")
    } | ConvertTo-Json
    
    $testSession | Set-Content $testSessionFile
    
    # Record session
    & $sessionRecordPath -SessionFile $testSessionFile -ErrorAction Stop | Out-Null
    
    # Verify entry was created
    $conversations = Get-Content $conversationHistoryPath | ForEach-Object { $_ | ConvertFrom-Json }
    $testConv = $conversations | Where-Object { $_.conversation_id -like "*$testSessionId*" }
    
    Test-Result -TestName "Session recording creates entry" `
        -Passed ($null -ne $testConv) `
        -Details "Session ID: $testSessionId"
    
    # Cleanup
    Remove-Item $testSessionFile -ErrorAction SilentlyContinue
    
} catch {
    Test-Result -TestName "Session recording creates entry" `
        -Passed $false `
        -Details "Error: $_"
}

# Test 4: auto-brain-updater.ps1 enhanced with session recording
$autoBrainPath = "scripts\auto-brain-updater.ps1"
$autoBrainContent = Get-Content $autoBrainPath -Raw
$hasSessionCheck = $autoBrainContent -match "Check for Active Sessions"

Test-Result -TestName "auto-brain-updater.ps1 has session recording" `
    -Passed $hasSessionCheck `
    -Details "Searches for completed sessions and auto-records"

Write-Host ""

# ========================================
# TEST LAYER 1: Copilot Chat Import
# ========================================
Write-Host "💬 Layer 1: Copilot Chat Import" -ForegroundColor Yellow
Write-Host ""

# Test 1: import-copilot-chats.ps1 exists
$importScriptPath = "scripts\import-copilot-chats.ps1"
Test-Result -TestName "import-copilot-chats.ps1 exists" `
    -Passed (Test-Path $importScriptPath) `
    -Details "Path: $importScriptPath"

# Test 2: Copilot Chat import works (dry run)
try {
    # Create test CopilotChats.txt
    $testCopilotPath = ".github\workflows\CopilotChats.txt"
    $testCopilotDir = Split-Path $testCopilotPath -Parent
    
    if (-not (Test-Path $testCopilotDir)) {
        New-Item -ItemType Directory -Path $testCopilotDir -Force | Out-Null
    }
    
    $testContent = @"
---
User: Can you help me create a test?
Assistant: Sure! I'll create a test for you.
User: Make it comprehensive
Assistant: Here's a comprehensive test...
---
"@
    
    $testContent | Set-Content $testCopilotPath
    
    # Run import (dry run)
    & $importScriptPath -DryRun -ErrorAction Stop | Out-Null
    
    # If we got here without error, it worked
    Test-Result -TestName "Copilot Chat import parses file" `
        -Passed $true `
        -Details "Dry run completed successfully"
    
    # Cleanup
    Remove-Item $testCopilotPath -ErrorAction SilentlyContinue
    
} catch {
    Test-Result -TestName "Copilot Chat import parses file" `
        -Passed $false `
        -Details "Error: $_"
}

# Test 3: post-commit hook has Copilot Chat detection
$postCommitPath = "hooks\post-commit"
$postCommitContent = Get-Content $postCommitPath -Raw
$hasCopilotCheck = $postCommitContent -match "Copilot Chat detected"

Test-Result -TestName "post-commit hook detects Copilot Chats" `
    -Passed $hasCopilotCheck `
    -Details "Hook checks for .github/workflows/CopilotChats.txt changes"

Write-Host ""

# ========================================
# TEST MONITORING: Health Checks
# ========================================
Write-Host "📊 Monitoring: Health Checks" -ForegroundColor Yellow
Write-Host ""

# Test 1: monitor-tier1-health.ps1 exists
$monitorScriptPath = "scripts\monitor-tier1-health.ps1"
Test-Result -TestName "monitor-tier1-health.ps1 exists" `
    -Passed (Test-Path $monitorScriptPath) `
    -Details "Path: $monitorScriptPath"

# Test 2: Health monitoring works
try {
    & $monitorScriptPath -ErrorAction Stop | Out-Null
    
    # If we got here without error, it worked
    Test-Result -TestName "Health monitoring runs" `
        -Passed $true `
        -Details "Generates utilization report"
    
} catch {
    Test-Result -TestName "Health monitoring runs" `
        -Passed $false `
        -Details "Error: $_"
}

# Test 3: tier1-health-report.ps1 exists
$reportScriptPath = "scripts\tier1-health-report.ps1"
Test-Result -TestName "tier1-health-report.ps1 exists" `
    -Passed (Test-Path $reportScriptPath) `
    -Details "Path: $reportScriptPath"

Write-Host ""

# ========================================
# SUMMARY
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Passed: $testsPassed" -ForegroundColor Green
Write-Host "  Failed: $testsFailed" -ForegroundColor $(if ($testsFailed -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($testsFailed -eq 0) {
    Write-Host "✅ All Tier 1 tracking tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Run: .\scripts\monitor-tier1-health.ps1" -ForegroundColor White
    Write-Host "  2. Check: kds-brain\conversation-history.jsonl" -ForegroundColor White
    Write-Host "  3. Commit changes to trigger post-commit hook" -ForegroundColor White
    Write-Host ""
    exit 0
} else {
    Write-Host "⚠️  Some tests failed - review errors above" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
