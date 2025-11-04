<#
.SYNOPSIS
    Week 1 Validation Tests - Bootstrap Brain Hemispheres

.DESCRIPTION
    Validates that Week 1 implementation is complete and working:
    - Hemisphere directory structure
    - Coordination queue messaging
    - Challenge protocol
    - Left brain execution logging
    - Right brain planning storage
    
.NOTES
    Version: 6.0.0-Week1
    Part of: KDS v6.0 Progressive Intelligence Implementation
    Success Criteria: All tests pass = Brain can help build Week 2
#>

$ErrorActionPreference = "Stop"

# Paths
$workspaceRoot = "D:\PROJECTS\KDS"
$kdsRoot = $workspaceRoot

# Test counters
$global:TestsPassed = 0
$global:TestsFailed = 0
$global:FailedTests = @()

function Test-Condition {
    param(
        [string]$Name,
        [scriptblock]$Condition,
        [string]$ErrorMessage
    )
    
    Write-Host "  Testing: $Name..." -NoNewline
    
    try {
        $result = & $Condition
        if ($result) {
            Write-Host " ✅ PASS" -ForegroundColor Green
            $global:TestsPassed++
            return $true
        } else {
            Write-Host " ❌ FAIL" -ForegroundColor Red
            Write-Host "    Reason: $ErrorMessage" -ForegroundColor Yellow
            $global:TestsFailed++
            $global:FailedTests += $Name
            return $false
        }
    } catch {
        Write-Host " ❌ ERROR" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Yellow
        $global:TestsFailed++
        $global:FailedTests += $Name
        return $false
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  KDS v6.0 Week 1 Validation Tests" -ForegroundColor Cyan
Write-Host "  Bootstrap Brain Hemispheres" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Test Group 1: Hemisphere Structure
Write-Host "Test Group 1: Hemisphere Directory Structure" -ForegroundColor Yellow
Write-Host ""

Test-Condition -Name "Left hemisphere directory exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "kds-brain\left-hemisphere") } `
    -ErrorMessage "Directory KDS/kds-brain/left-hemisphere not found"

Test-Condition -Name "Right hemisphere directory exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "kds-brain\right-hemisphere") } `
    -ErrorMessage "Directory KDS/kds-brain/right-hemisphere not found"

Test-Condition -Name "Corpus callosum directory exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "kds-brain\corpus-callosum") } `
    -ErrorMessage "Directory KDS/kds-brain/corpus-callosum not found"

Test-Condition -Name "Left hemisphere execution state file exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "kds-brain\left-hemisphere\execution-state.jsonl") } `
    -ErrorMessage "File execution-state.jsonl not found"

Test-Condition -Name "Right hemisphere active plan file exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "kds-brain\right-hemisphere\active-plan.yaml") } `
    -ErrorMessage "File active-plan.yaml not found"

Test-Condition -Name "Right hemisphere planning state file exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "kds-brain\right-hemisphere\planning-state.yaml") } `
    -ErrorMessage "File planning-state.yaml not found"

Test-Condition -Name "Coordination queue file exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "kds-brain\corpus-callosum\coordination-queue.jsonl") } `
    -ErrorMessage "File coordination-queue.jsonl not found"

Write-Host ""

# Test Group 2: Coordination Queue Functionality
Write-Host "Test Group 2: Coordination Queue Messaging" -ForegroundColor Yellow
Write-Host ""

# Clean queue first
& (Join-Path $kdsRoot "scripts\corpus-callosum\clear-queue.ps1") -All | Out-Null

Test-Condition -Name "Send message script exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "scripts\corpus-callosum\send-message.ps1") } `
    -ErrorMessage "Script send-message.ps1 not found"

Test-Condition -Name "Receive message script exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "scripts\corpus-callosum\receive-message.ps1") } `
    -ErrorMessage "Script receive-message.ps1 not found"

# Test message sending and receiving
$testMessage = @{
    task_id = "test-1.1"
    status = "test"
}

& (Join-Path $kdsRoot "scripts\corpus-callosum\send-message.ps1") `
    -From "right" `
    -To "left" `
    -Type "planning_update" `
    -Data $testMessage `
    2>&1 | Out-Null

Test-Condition -Name "Can send message from right to left" `
    -Condition { 
        $queueContent = Get-Content (Join-Path $kdsRoot "kds-brain\corpus-callosum\coordination-queue.jsonl")
        $queueContent.Count -gt 0
    } `
    -ErrorMessage "Message not written to queue"

$receiveResult = & (Join-Path $kdsRoot "scripts\corpus-callosum\receive-message.ps1") `
    -For "left" `
    -MarkProcessed $true `
    2>&1

Test-Condition -Name "Can receive message for left hemisphere" `
    -Condition { 
        $receiveResult.Count -gt 0 -and $receiveResult[0].type -eq "planning_update"
    } `
    -ErrorMessage "No messages received or wrong type"

Test-Condition -Name "Received message contains correct data" `
    -Condition { 
        $receiveResult[0].data.task_id -eq "test-1.1"
    } `
    -ErrorMessage "Message data incorrect"

Test-Condition -Name "Message marked as processed" `
    -Condition { 
        $receiveResult[0].processed -eq $true
    } `
    -ErrorMessage "Message not marked as processed"

Write-Host ""

# Test Group 3: Challenge Protocol
Write-Host "Test Group 3: Challenge Protocol (Tier 0)" -ForegroundColor Yellow
Write-Host ""

Test-Condition -Name "Challenge protocol rule file exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "governance\rules\challenge-user-changes.md") } `
    -ErrorMessage "File challenge-user-changes.md not found"

Test-Condition -Name "Challenges log file exists" `
    -Condition { Test-Path (Join-Path $kdsRoot "governance\challenges.jsonl") } `
    -ErrorMessage "File challenges.jsonl not found"

$challengeRule = Get-Content (Join-Path $kdsRoot "governance\rules\challenge-user-changes.md") -Raw

Test-Condition -Name "Challenge rule defines TDD violations" `
    -Condition { 
        $challengeRule -match "TDD_WORKFLOW" -and $challengeRule -match "Skip.*test"
    } `
    -ErrorMessage "TDD workflow violations not defined"

Test-Condition -Name "Challenge rule defines OVERRIDE protocol" `
    -Condition { 
        $challengeRule -match "OVERRIDE" -and $challengeRule -match "justification"
    } `
    -ErrorMessage "Override protocol not defined"

Write-Host ""

# Test Group 4: Agent Updates
Write-Host "Test Group 4: Agent Hemisphere Integration" -ForegroundColor Yellow
Write-Host ""

$codeExecutor = Get-Content (Join-Path $kdsRoot "prompts\internal\code-executor.md") -Raw

Test-Condition -Name "Code executor identifies as LEFT hemisphere" `
    -Condition { 
        $codeExecutor -match "Brain Hemisphere.*LEFT"
    } `
    -ErrorMessage "Code executor doesn't identify hemisphere"

Test-Condition -Name "Code executor has execution logging" `
    -Condition { 
        $codeExecutor -match "execution-state\.jsonl" -and 
        $codeExecutor -match "Log.*left hemisphere"
    } `
    -ErrorMessage "Code executor missing execution logging"

$workPlanner = Get-Content (Join-Path $kdsRoot "prompts\internal\work-planner.md") -Raw

Test-Condition -Name "Work planner identifies as RIGHT hemisphere" `
    -Condition { 
        $workPlanner -match "Brain Hemisphere.*RIGHT"
    } `
    -ErrorMessage "Work planner doesn't identify hemisphere"

Test-Condition -Name "Work planner has right hemisphere storage" `
    -Condition { 
        $workPlanner -match "active-plan\.yaml" -and 
        $workPlanner -match "planning-state\.yaml"
    } `
    -ErrorMessage "Work planner missing right hemisphere storage"

Write-Host ""

# Test Group 5: Coordination Capability
Write-Host "Test Group 5: Cross-Hemisphere Coordination" -ForegroundColor Yellow
Write-Host ""

# Clean queue
& (Join-Path $kdsRoot "scripts\corpus-callosum\clear-queue.ps1") -All | Out-Null

# Send message from left to right
& (Join-Path $kdsRoot "scripts\corpus-callosum\send-message.ps1") `
    -From "left" `
    -To "right" `
    -Type "execution_complete" `
    -Data @{task_id="1.1"; success=$true} `
    2>&1 | Out-Null

# Send message from right to left
& (Join-Path $kdsRoot "scripts\corpus-callosum\send-message.ps1") `
    -From "right" `
    -To "left" `
    -Type "planning_update" `
    -Data @{task_id="1.2"} `
    2>&1 | Out-Null

Test-Condition -Name "Can coordinate bidirectionally" `
    -Condition { 
        $leftMessages = & (Join-Path $kdsRoot "scripts\corpus-callosum\receive-message.ps1") -For "left" -MarkProcessed $false 2>&1
        $rightMessages = & (Join-Path $kdsRoot "scripts\corpus-callosum\receive-message.ps1") -For "right" -MarkProcessed $false 2>&1
        ($leftMessages.Count -gt 0) -and ($rightMessages.Count -gt 0)
    } `
    -ErrorMessage "Bidirectional messaging not working"

Test-Condition -Name "Messages route to correct hemisphere" `
    -Condition { 
        $leftMsg = & (Join-Path $kdsRoot "scripts\corpus-callosum\receive-message.ps1") -For "left" -MarkProcessed $false -Latest 2>&1
        $rightMsg = & (Join-Path $kdsRoot "scripts\corpus-callosum\receive-message.ps1") -For "right" -MarkProcessed $false -Latest 2>&1
        ($leftMsg[0].to -eq "left") -and ($rightMsg[0].to -eq "right")
    } `
    -ErrorMessage "Messages not routed correctly"

Write-Host ""

# Test Group 6: Week 1 Capability Checklist
Write-Host "Test Group 6: Week 1 Capability Validation" -ForegroundColor Yellow
Write-Host ""

Test-Condition -Name "Brain can route requests to hemispheres" `
    -Condition { 
        # Check that both hemispheres have clear identities
        $leftIdentity = $codeExecutor -match "LEFT.*Precise.*analytical"
        $rightIdentity = $workPlanner -match "RIGHT.*Strategic.*holistic"
        $leftIdentity -and $rightIdentity
    } `
    -ErrorMessage "Hemisphere routing not clearly defined"

Test-Condition -Name "Brain can log execution state" `
    -Condition { 
        # Execution logging present in code-executor
        $codeExecutor -match "execution-state\.jsonl" -and 
        $codeExecutor -match "phase.*RED|GREEN|REFACTOR"
    } `
    -ErrorMessage "Execution state logging incomplete"

Test-Condition -Name "Brain can create basic plans" `
    -Condition { 
        # Planning capability in work-planner
        $workPlanner -match "active-plan\.yaml" -and 
        $workPlanner -match "phases"
    } `
    -ErrorMessage "Planning capability incomplete"

Test-Condition -Name "Brain can challenge risky proposals" `
    -Condition { 
        # Challenge protocol exists and is comprehensive
        $challengeRule -match "CHALLENGE" -and 
        $challengeRule -match "TDD_WORKFLOW|ARCHITECTURE|BRAIN_INTEGRITY"
    } `
    -ErrorMessage "Challenge protocol incomplete"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Summary
Write-Host ""
if ($global:TestsFailed -eq 0) {
    Write-Host "✅ ALL TESTS PASSED! ($global:TestsPassed/$($global:TestsPassed + $global:TestsFailed))" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 Week 1 Implementation COMPLETE!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Brain Capabilities After Week 1:" -ForegroundColor Cyan
    Write-Host "  ✅ Can route requests to appropriate hemisphere" -ForegroundColor Green
    Write-Host "  ✅ Can log execution state" -ForegroundColor Green
    Write-Host "  ✅ Can create basic plans" -ForegroundColor Green
    Write-Host "  ✅ Can challenge risky user proposals" -ForegroundColor Green
    Write-Host "  ❌ Cannot run TDD automatically (Week 2)" -ForegroundColor Yellow
    Write-Host "  ❌ Cannot match patterns (Week 3)" -ForegroundColor Yellow
    Write-Host "  ❌ Cannot learn from execution (Week 4)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next Step: Brain can now help plan Week 2 implementation!" -ForegroundColor Cyan
    Write-Host ""
    exit 0
} else {
    Write-Host "❌ TESTS FAILED: $global:TestsFailed failed, $global:TestsPassed passed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Failed Tests:" -ForegroundColor Yellow
    foreach ($test in $global:FailedTests) {
        Write-Host "  - $test" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "⚠️  Week 1 implementation incomplete. Fix failing tests before proceeding." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
