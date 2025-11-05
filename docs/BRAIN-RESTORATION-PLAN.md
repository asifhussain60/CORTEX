# KDS BRAIN Complete Restoration Plan

**Date:** 2025-11-05  
**Version:** 1.0  
**Status:** 🔴 CRITICAL - BRAIN Operating at ~5% Capacity  
**Goal:** Restore BRAIN to 100% functionality with comprehensive verification

---

## Executive Summary

### Current State: CRITICAL FAILURE 🚨

Based on comprehensive self-review (see `#file:CopilotContext.txt`), the KDS BRAIN is experiencing **severe anterograde amnesia** - it can access old knowledge but cannot form new memories.

**Failure Breakdown:**
- ❌ **Tier 1 (STM):** Conversation capture stopped at 08:09 AM - 4+ hours of work lost
- ❌ **Tier 2 (LTM):** Zero new patterns learned from today's work (18K+ lines of code)
- ❌ **Tier 3 (Context):** All metrics show zero/stale data despite active development
- ❌ **Tier 4 (Events):** Events logged but NOT analyzed or promoted to knowledge
- ❌ **Tier 5 (Hemispheres):** Left hemisphere empty, Right hemisphere has wrong plan
- ❌ **Corpus Callosum:** Zero LEFT↔RIGHT coordination messages
- ❌ **Git Commits:** 17 uncommitted files, 2+ hours of work not in version control
- ❌ **TDD Enforcement:** Brain Protector dormant, no challenges to violations
- ❌ **Runtime Errors:** App crashes with 40+ exceptions despite build success

**Knowledge Retention Rate:** ~5% (95% of today's work lost to amnesia)

---

## Restoration Philosophy

### The "Hospital Triage" Approach

1. **Stop the Bleeding** (Phase 1): Fix critical infrastructure preventing ANY learning
2. **Stabilize the Patient** (Phase 2): Restore basic BRAIN functions
3. **Rehabilitation** (Phase 3): Restore advanced capabilities
4. **Stress Testing** (Phase 4): Verify under realistic workload
5. **Monitoring** (Phase 5): Continuous health validation

### Success Criteria

**BRAIN is 100% functional when:**
- ✅ All 3 conversation recording layers capture work automatically
- ✅ Events are analyzed and promoted to knowledge graph within 1 hour
- ✅ Development context reflects actual work within 15 minutes
- ✅ Left hemisphere tracks execution state for every task
- ✅ Right hemisphere updates strategic plan daily
- ✅ Corpus callosum coordinates LEFT↔RIGHT every hour
- ✅ Git commits happen automatically after task completion
- ✅ Brain Protector challenges TDD/SOLID violations immediately
- ✅ Stress test of 10 diverse tasks results in 100% knowledge retention

---

## Phase 1: Critical Infrastructure Repair (STOP THE BLEEDING)

**Goal:** Fix the root causes preventing ANY BRAIN learning  
**Duration:** 2-3 hours  
**Success:** BRAIN can capture new events and conversations

### 1.1 Fix Tier 1 Auto-Recording ❌→✅

**Problem:** Conversation capture stopped at 08:09 AM

**Root Cause Analysis:**
```powershell
# Test each recording layer
.\scripts\import-copilot-chats.ps1 -DryRun  # Layer 1: Copilot Chat
.\scripts\record-session-conversation.ps1 -SessionFile "sessions/test.json"  # Layer 2: Sessions
# Layer 3: Manual (record-conversation.ps1) - MISSING FILE
```

**Fixes Required:**

#### 1.1.1 Create Missing `record-conversation.ps1`
```powershell
# File: d:\PROJECTS\KDS\scripts\record-conversation.ps1
# Purpose: Layer 3 manual recording for critical conversations
# Status: ❌ FILE DOES NOT EXIST (referenced in docs but missing)
```

**Action:** Create comprehensive manual recording script with:
- Title, Intent, Entities, Files, Outcome parameters
- Validation of required fields
- Append to conversation-history.jsonl
- Avoid duplicates (check conversation_id)
- Support for --DryRun testing

#### 1.1.2 Fix Copilot Chat Import (Layer 1)
**Test:** Check if `.github/workflows/CopilotChats.txt` exists and is parseable
```powershell
Test-Path ".github\workflows\CopilotChats.txt"
Get-Content ".github\workflows\CopilotChats.txt" | Select-Object -First 20
```

**Expected Issues:**
- File may not exist (Copilot Chat export not configured)
- Format may have changed (parser broken)

**Fix:** Update `import-copilot-chats.ps1` parser or document manual export process

#### 1.1.3 Fix Session Recording (Layer 2)
**Test:** Verify `auto-brain-updater.ps1` calls `record-session-conversation.ps1`
```powershell
# Check auto-brain-updater.ps1 lines 140-160
# Verify session detection logic works
```

**Fix:** Ensure session recording triggers on session completion

#### 1.1.4 Fix Post-Commit Hook
**Test:** Verify hook executes after git commit
```bash
# Check hooks/post-commit is executable
# Test: Make dummy commit, verify hook runs
```

**Fix:** Ensure hook calls all 3 recording layers

**Validation:**
```powershell
# After fixes, create test conversation
.\scripts\record-conversation.ps1 -Title "BRAIN Test" -Intent "TEST" -Outcome "Testing Layer 3"

# Verify in conversation-history.jsonl
$lastConv = Get-Content "kds-brain\conversation-history.jsonl" | 
    Select-Object -Last 1 | ConvertFrom-Json
Write-Host "Last conversation: $($lastConv.title)"
```

### 1.2 Fix Event Processing (Tier 4 → Tier 2 Transfer) ❌→✅

**Problem:** 40+ events logged but zero patterns extracted

**Root Cause:** No automatic event analysis pipeline

**Fixes Required:**

#### 1.2.1 Create Event Pattern Analyzer
```powershell
# File: scripts\analyze-event-patterns.ps1
# Purpose: Read events.jsonl, detect patterns, update knowledge-graph.yaml
```

**Patterns to Detect:**
1. **Repeated Errors** (same error 3+ times → create knowledge entry)
2. **File Co-Modifications** (files changed together → file_relationships)
3. **Workflow Sequences** (task sequences → workflow_templates)
4. **Validation Failures** (common build/test failures → validation_insights)

#### 1.2.2 Update `brain-updater.ps1` to Call Analyzer
```powershell
# Add to brain-updater.ps1 after event collection:
if ($newEvents.Count -ge 10) {
    & ".\scripts\analyze-event-patterns.ps1" -EventsFile $eventsPath -OutputPath $kgPath
}
```

#### 1.2.3 Fix `auto-brain-updater.ps1` Thresholds
**Current:** 50 events OR 24 hours  
**Problem:** Too high - 50 events takes days to accumulate

**Fix:** Lower thresholds for active development
```powershell
$eventThresholdMet = $eventCount -ge 20  # Was: 50
$timeThresholdMet = $hoursSinceUpdate -ge 4  # Was: 24
```

**Validation:**
```powershell
# Generate 20+ test events
1..25 | ForEach-Object {
    .\scripts\log-event.ps1 -EventType "test_event" -EventData @{
        test_id = $_
        message = "BRAIN restoration test event $_"
    }
}

# Trigger auto-brain-updater
.\scripts\auto-brain-updater.ps1 -RequestSummary "Test" -ResponseType "test"

# Verify knowledge-graph.yaml updated
$kgLastUpdated = (Get-Content "kds-brain\knowledge-graph.yaml" -Raw) -match "last_updated:\s*(.+)"
Write-Host "Knowledge graph last updated: $($Matches[1])"
```

### 1.3 Fix Development Context Collection (Tier 3) ❌→✅

**Problem:** All metrics show zero despite active development

**Root Cause:** `collect-development-context.ps1` not collecting real data

**Fixes Required:**

#### 1.3.1 Test Collection Script
```powershell
.\scripts\collect-development-context.ps1 -Verbose

# Check output in development-context.yaml
$devContext = Get-Content "kds-brain\development-context.yaml" -Raw | ConvertFrom-Yaml
$devContext.git_activity.last_30_days
```

**Expected Issues:**
- Git log parsing broken
- File change analysis not working
- Metrics defaulting to zero

#### 1.3.2 Fix Git Activity Collection
```powershell
# Fix git log command
git log --since="30 days ago" --pretty=format:"%h|%an|%ae|%ad|%s" --numstat --date=iso

# Verify parsing logic in collect-development-context.ps1
```

#### 1.3.3 Fix Code Changes Metrics
```powershell
# Get actual file changes
git diff --numstat HEAD~30 HEAD

# Update lines_added, lines_deleted, files_modified
```

#### 1.3.4 Trigger Collection After Every BRAIN Update
```powershell
# Add to brain-updater.ps1 (end of script):
& ".\scripts\collect-development-context.ps1"
```

**Validation:**
```powershell
# Force collection
.\scripts\collect-development-context.ps1 -Force

# Verify non-zero metrics
$devContext = Get-Content "kds-brain\development-context.yaml" -Raw | ConvertFrom-Yaml
if ($devContext.git_activity.last_30_days.total_commits -eq 0) {
    Write-Host "❌ Collection still broken"
} else {
    Write-Host "✅ Collection working: $($devContext.git_activity.last_30_days.total_commits) commits"
}
```

### 1.4 Commit Uncommitted Work ❌→✅

**Problem:** 17 files uncommitted, 2+ hours of work at risk

**Immediate Action:**
```powershell
# Stage all work
git add .

# Create semantic commit
git commit -m "feat(dashboard): Complete V8 Phase 2 Features Tab with scanner and test runner

- Add FeatureScannerService (18K lines) - scans prompts/scripts/brain for features
- Add TestRunner service (10K lines) - automated test execution with caching
- Add FeaturesViewModel with real-time feature discovery
- Add BoolToVisibilityConverter, CountToVisibilityConverter, StringToVisibilityConverter
- Add ApplicationLaunchTests, TestRunnerTests, HeartbeatAnimationTests
- Update DashboardViewModel with test runner integration
- Update ActivityViewModel with features tab support

Known Issues:
- ConversationsViewModel JSON parsing error (GitCommit.Message array vs string)
- DashboardViewModel storyboard BeginStoryboardName missing
- TestRunner needs completion verification

Tests: Partial (FeatureScannerService missing tests)
Docs: V8-PHASE-2-FEATURES-TAB-COMPLETE.md
Phase: V8 Phase 2"

# Push to prevent data loss
git push
```

**Validation:**
```powershell
# Verify clean working directory
git status

# Should show: "nothing to commit, working tree clean"
```

---

## Phase 2: Restore Basic BRAIN Functions (STABILIZE)

**Goal:** Restore all 6 BRAIN tiers to basic functionality  
**Duration:** 4-5 hours  
**Success:** BRAIN can learn from new work immediately

### 2.1 Restore Tier 5: Brain Hemispheres ❌→✅

#### 2.1.1 Initialize Left Hemisphere (Execution State)

**Problem:** `execution-state.jsonl` completely empty

**Fix:** Create initialization script
```powershell
# File: scripts\init-left-hemisphere.ps1
# Purpose: Initialize execution state tracking
```

**Schema to Implement:**
```jsonl
{"timestamp":"2025-11-05T12:00:00Z","task_id":"task-001","phase":"RED","action":"create_test","files_modified":["Tests/TestFile.cs"],"tests_status":"fail","rollback_point":"abc123","success":true,"error":null}
```

**Integration Points:**
- Test-generator agent → Log RED phase
- Code-executor agent → Log GREEN phase
- Code-executor agent → Log REFACTOR phase
- Health-validator agent → Log VALIDATE phase

**Action:** Add logging to each agent's workflow

#### 2.1.2 Update Right Hemisphere (Strategic Plan)

**Problem:** `active-plan.yaml` shows "Week 2: Left Brain TDD Automation" (Nov 4) but actual work is "V8 Phase 2 Features Tab" (Nov 5)

**Fix:** Update plan to reality
```yaml
# File: kds-brain/right-hemisphere/active-plan.yaml
current_phase: "V8 Phase 2: Advanced Dashboard Features"
plan_updated: "2025-11-05T18:00:00Z"
next_objectives:
  - "Fix runtime errors (JSON parsing, storyboard)"
  - "Complete FeatureScannerService tests"
  - "V8 Phase 3: Cleanup Scripts"
```

**Automation:** Create script to update plan from git commits
```powershell
# scripts\sync-strategic-plan.ps1
# Read recent commits → infer current work → update active-plan.yaml
```

#### 2.1.3 Activate Corpus Callosum

**Problem:** Zero LEFT↔RIGHT coordination messages

**Fix:** Create coordination script
```powershell
# File: scripts\coordinate-brain-hemispheres.ps1
# Purpose: Sync LEFT execution state with RIGHT strategic plan
```

**Coordination Logic:**
```powershell
# Every hour:
# 1. Read LEFT execution-state.jsonl (last 10 tasks)
# 2. Read RIGHT active-plan.yaml (current objectives)
# 3. Detect misalignment (executing tasks not in plan)
# 4. Log coordination event
# 5. Update RIGHT plan if LEFT deviated significantly
```

**Validation:**
```powershell
# After running coordination script
$coordEvents = Get-Content "kds-brain\corpus-callosum\coordination-queue.jsonl" |
    ConvertFrom-Json

if ($coordEvents.Count -eq 0) {
    Write-Host "❌ Corpus callosum still inactive"
} else {
    Write-Host "✅ Coordination working: $($coordEvents.Count) messages"
}
```

### 2.2 Fix Git Commit Automation ❌→✅

**Problem:** Commits not happening automatically

**Root Cause:** Commit-handler agent not invoked

**Fixes Required:**

#### 2.2.1 Create Auto-Commit Script
```powershell
# File: scripts\auto-commit-if-ready.ps1
# Purpose: Check if work is ready to commit, then commit
```

**Readiness Checks:**
- ✅ Build succeeds (`dotnet build`)
- ✅ Tests pass (run all tests)
- ✅ Zero errors/warnings
- ✅ Files staged or modified

**Commit Logic:**
- Generate semantic commit message from changes
- Include test status, docs status
- Auto-push if on main branch

#### 2.2.2 Trigger After Task Completion
```powershell
# Add to work-planner agent (end of task):
Write-Host "Task complete - checking commit readiness..."
& ".\scripts\auto-commit-if-ready.ps1"
```

#### 2.2.3 Add to Auto-Brain-Updater
```powershell
# Add to auto-brain-updater.ps1:
if ($ResponseType -eq "execute" -and $AgentInvoked -in @("code-executor", "test-generator")) {
    & ".\scripts\auto-commit-if-ready.ps1"
}
```

**Validation:**
```powershell
# Make a small change
Add-Content -Path "README.md" -Value "`n<!-- BRAIN restoration test -->"

# Trigger auto-commit
.\scripts\auto-commit-if-ready.ps1

# Verify commit created
git log -1 --oneline
# Should show new commit with semantic message
```

### 2.3 Activate Brain Protector (TDD Enforcement) ❌→✅

**Problem:** Brain Protector dormant - no challenges to TDD violations

**Root Cause:** Not invoked before code execution

**Fixes Required:**

#### 2.3.1 Add Brain Protector to Code-Executor Agent
```markdown
# File: prompts/internal/code-executor.md
# Add BEFORE Step 2 (Implementation):

## Step 1.5: Validate TDD Compliance

Invoke Brain Protector to challenge if tests don't exist:
#file:KDS/prompts/internal/brain-protector.md

Request: Implement {feature} without tests
```

#### 2.3.2 Add to Work-Planner Agent
```markdown
# File: prompts/internal/work-planner.md
# Add to Phase Planning:

For each phase, validate:
- RED: Test file created FIRST
- GREEN: Implementation SECOND
- REFACTOR: Cleanup THIRD

If user requests implementation without tests:
#file:KDS/prompts/internal/brain-protector.md
```

#### 2.3.3 Create Pre-Execution Hook
```powershell
# File: scripts\validate-tdd-before-execution.ps1
# Purpose: Check if tests exist before allowing implementation
```

**Validation:**
```powershell
# Test: Try to implement code without test
# Expected: Brain Protector challenges

# Actual test (create dummy scenario):
# User: "Implement UserService.CreateUser() method"
# Expected: "⚠️ TDD VIOLATION: No test file found. Create UserServiceTests.cs first."
```

### 2.4 Fix Runtime Error Detection ❌→✅

**Problem:** Build succeeds but app crashes at runtime

**Root Cause:** No integration tests that actually run the app

**Fixes Required:**

#### 2.4.1 Create Runtime Validation Script
```powershell
# File: scripts\validate-runtime-health.ps1
# Purpose: Actually run the app, check for errors
```

**Validation Steps:**
1. Build app (`dotnet build`)
2. Start app in background
3. Wait for initialization
4. Check events.jsonl for dashboard_error entries (last 1 minute)
5. If errors found, report as FAILED
6. Stop app

#### 2.4.2 Add to Definition of DONE
```markdown
# Update: governance/rules.md

Definition of DONE:
- ✅ Zero compilation errors
- ✅ Zero warnings
- ✅ All tests pass
- ✅ App runs without runtime errors (NEW)
```

#### 2.4.3 Integrate with Auto-Commit
```powershell
# Update: scripts\auto-commit-if-ready.ps1
# Add runtime validation BEFORE commit

& ".\scripts\validate-runtime-health.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Runtime errors detected - commit blocked"
    exit 1
}
```

**Validation:**
```powershell
# Test with current code (known runtime errors)
.\scripts\validate-runtime-health.ps1

# Expected: FAIL (JSON parsing error, storyboard error)

# Fix errors, test again
# Expected: PASS
```

---

## Phase 3: Restore Advanced Capabilities (REHABILITATION)

**Goal:** Restore sophisticated BRAIN learning and prediction  
**Duration:** 3-4 hours  
**Success:** BRAIN provides proactive insights and warnings

### 3.1 Implement Pattern Recognition (Tier 4 → Tier 2)

**Create:** `scripts\extract-patterns-from-events.ps1`

**Patterns to Extract:**

#### 3.1.1 Error Patterns
```yaml
# From: 40+ ConversationsViewModel JSON errors
wpf_json_deserialization_error:
  issue: "JsonException when deserializing multi-line commit messages"
  symptom: "StartArray cannot convert to String"
  cause: "GitCommit.Message property is string but JSON has array"
  fix: "Change Message to List<string> or serialize as single string"
  frequency: 40
  last_seen: "2025-11-05T12:41:47"
  confidence: 1.0
```

#### 3.1.2 Workflow Patterns
```yaml
# From: Features tab implementation sequence
features_tab_workflow:
  pattern: "scanner_service → viewmodel → tests → integration"
  success_rate: 0.75  # (build passed, but runtime errors)
  components:
    - FeatureScannerService
    - FeaturesViewModel
    - TestRunner
    - Converters
  challenges:
    - Multi-line commit parsing
    - Storyboard animation naming
  confidence: 0.85
```

#### 3.1.3 File Relationship Patterns
```yaml
# From: Co-modifications today
file_relationships:
  FeaturesViewModel.cs:
    common_changes_with:
      FeatureScannerService.cs: 1.0  # Always changed together
      TestRunner.cs: 0.8
      DashboardViewModel.cs: 0.6
```

### 3.2 Implement Proactive Warnings (Tier 3)

**Create:** `scripts\generate-proactive-warnings.ps1`

**Warning Types:**

#### 3.2.1 File Hotspot Warnings
```yaml
# Detect files changed frequently (instability)
warnings:
  - type: file_hotspot
    file: "ConversationsViewModel.cs"
    churn_rate: 0.35  # 35% of commits touch this file
    recommendation: "Extra testing, smaller changes"
```

#### 3.2.2 Pattern Match Warnings
```yaml
# Detect known error patterns in uncommitted code
warnings:
  - type: pattern_match
    pattern: "wpf_json_deserialization_error"
    file: "DataModels.cs"
    line: 45
    recommendation: "Change GitCommit.Message to List<string>"
```

#### 3.2.3 Test Coverage Warnings
```yaml
# Detect files without tests
warnings:
  - type: missing_tests
    file: "FeatureScannerService.cs"
    size: 18014  # Large file without tests
    recommendation: "Create FeatureScannerServiceTests.cs"
```

### 3.3 Implement BRAIN Query Interface

**Create:** `scripts\query-brain.ps1`

**Query Capabilities:**
```powershell
# Query knowledge graph
.\scripts\query-brain.ps1 -Pattern "json_deserialization"
# Returns: All known JSON errors and fixes

.\scripts\query-brain.ps1 -File "ConversationsViewModel.cs"
# Returns: File relationships, error history, modification patterns

.\scripts\query-brain.ps1 -Workflow "ui_component"
# Returns: Best practices for creating UI components

.\scripts\query-brain.ps1 -Recent -Days 7
# Returns: Learnings from last 7 days
```

---

## Phase 4: Comprehensive Verification System (STRESS TEST)

**Goal:** Prove BRAIN works under realistic workload  
**Duration:** 2-3 hours  
**Success:** 100% knowledge retention on 10 diverse tasks

### 4.1 Design BRAIN Stress Test Scenarios

**Create:** `tests\brain-stress-test-scenarios.yaml`

```yaml
scenarios:
  - id: scenario_01_simple_bug_fix
    title: "Simple Bug Fix"
    description: "Fix typo in existing file"
    tasks:
      - "Fix typo in README.md line 45"
    expected_learning:
      - tier_1: "Conversation captured with intent=CORRECT"
      - tier_2: "No new pattern (too simple)"
      - tier_4: "Event logged: file_modified"
      - tier_5_left: "Execution state: VALIDATE → GREEN"
    expected_commits: 1

  - id: scenario_02_new_feature_tdd
    title: "New Feature with TDD"
    description: "Add new service method using TDD"
    tasks:
      - "Create CalculatorService.Add() method using TDD"
    expected_learning:
      - tier_1: "Conversation captured with intent=PLAN, then EXECUTE"
      - tier_2: "Pattern: tdd_service_creation"
      - tier_4: "Events: test_created (RED), implementation_complete (GREEN)"
      - tier_5_left: "RED → GREEN → REFACTOR cycle"
      - tier_5_right: "Plan updated with calculator feature"
      - brain_protector: "No challenges (TDD followed)"
    expected_commits: 1

  - id: scenario_03_tdd_violation
    title: "TDD Violation Attempt"
    description: "Try to implement without test"
    tasks:
      - "Implement UserService.Delete() without test"
    expected_learning:
      - brain_protector: "Challenge issued: 'Create test first'"
      - tier_4: "Event: tdd_violation_challenged"
    expected_commits: 0  # Blocked

  - id: scenario_04_multi_file_feature
    title: "Multi-File Feature"
    description: "Feature spanning service, viewmodel, view"
    tasks:
      - "Add user profile feature (Service + ViewModel + View)"
    expected_learning:
      - tier_1: "Conversation captured (multi-phase)"
      - tier_2: "File relationships: ProfileService.cs + ProfileViewModel.cs + ProfileView.xaml"
      - tier_4: "Events: multiple file_modified events"
      - tier_3: "Metrics updated: 3 files modified"
    expected_commits: 1

  - id: scenario_05_runtime_error
    title: "Runtime Error Introduction"
    description: "Introduce runtime error, detect, fix"
    tasks:
      - "Add code that compiles but crashes at runtime"
    expected_learning:
      - tier_4: "Event: dashboard_error logged"
      - tier_2: "Pattern extracted from repeated error"
      - runtime_validator: "Error detected before commit"
    expected_commits: 0  # Blocked until fixed

  - id: scenario_06_refactoring
    title: "Code Refactoring"
    description: "Refactor existing code for clarity"
    tasks:
      - "Extract method from DashboardViewModel.LoadData()"
    expected_learning:
      - tier_1: "Conversation: intent=REFACTOR"
      - tier_5_left: "Phase=REFACTOR logged"
      - tier_4: "Event: refactor_complete"
    expected_commits: 1

  - id: scenario_07_knowledge_reuse
    title: "Knowledge Graph Reuse"
    description: "Similar task to previous work"
    tasks:
      - "Add export button (similar to previous share button)"
    expected_learning:
      - tier_2: "Query finds 'share button' pattern"
      - tier_1: "Conversation references previous work"
      - faster_delivery: "Should be 50%+ faster than first time"
    expected_commits: 1

  - id: scenario_08_git_commit_tracking
    title: "Git Commit Association"
    description: "Conversation linked to commit"
    tasks:
      - "Add license header to all files"
    expected_learning:
      - tier_1: "Conversation has associated_commits populated"
      - tier_4: "Event: git_commit_associated"
    expected_commits: 1

  - id: scenario_09_brain_self_protection
    title: "Brain Self-Protection"
    description: "Attempt to modify brain files incorrectly"
    tasks:
      - "Add application path to knowledge-graph.yaml"
    expected_learning:
      - brain_protector: "Tier boundary violation detected"
      - tier_4: "Event: protection_triggered"
    expected_commits: 0  # Blocked

  - id: scenario_10_amnesia_recovery
    title: "Amnesia and Recovery"
    description: "Trigger amnesia, verify recovery"
    tasks:
      - "Run brain-amnesia.ps1"
      - "Verify Tier 0 preserved"
      - "Verify Tier 1-4 reset"
    expected_learning:
      - tier_0: "Unchanged (governance rules intact)"
      - tier_1: "Empty (conversations cleared)"
      - tier_2: "Tier 2 items deleted, Tier 0 preserved"
    expected_commits: 0
```

### 4.2 Create BRAIN Test Runner

**Create:** `tests\run-brain-stress-test.ps1`

```powershell
<#
.SYNOPSIS
Execute BRAIN stress test scenarios and validate learning

.DESCRIPTION
Runs 10 comprehensive scenarios to verify:
- All 6 BRAIN tiers functioning
- STM→LTM transfer working
- Event processing and pattern extraction
- Git commit automation
- TDD enforcement
- Runtime error detection
- Brain self-protection

.PARAMETER Scenario
Run specific scenario (1-10) or "all"

.PARAMETER Verbose
Show detailed learning validation

.EXAMPLE
.\tests\run-brain-stress-test.ps1 -Scenario all
Runs all 10 scenarios

.EXAMPLE
.\tests\run-brain-stress-test.ps1 -Scenario 2 -Verbose
Runs scenario 2 (TDD) with detailed output
#>

param(
    [string]$Scenario = "all",
    [switch]$Verbose
)

# Test execution logic
$results = @()

# For each scenario:
# 1. Take BRAIN snapshot (backup all tiers)
# 2. Execute scenario tasks
# 3. Wait for BRAIN processing (30 seconds)
# 4. Validate expected_learning
# 5. Record pass/fail
# 6. Restore BRAIN snapshot (for next test)

# Generate report
# - Scenarios passed/failed
# - Knowledge retention rate
# - Performance metrics
```

### 4.3 Create BRAIN Health Dashboard

**Create:** `scripts\generate-brain-health-report.ps1`

**Report Sections:**
1. **Tier Status** - All 6 tiers operational?
2. **Learning Rate** - Events → Patterns conversion %
3. **Memory Utilization** - Tier 1 usage, Tier 2 growth
4. **Coordination** - LEFT↔RIGHT sync frequency
5. **Protection** - Challenges issued by Brain Protector
6. **Knowledge Quality** - Pattern confidence distribution
7. **Automation Health** - Git commits, BRAIN updates, test runs

**Output:** HTML dashboard with charts

---

## Phase 5: Continuous Monitoring (LONG-TERM HEALTH)

**Goal:** Prevent future BRAIN degradation  
**Duration:** 1 hour  
**Success:** Automated health checks detect issues within 5 minutes

### 5.1 Create BRAIN Health Monitor

**Create:** `scripts\monitor-brain-health.ps1`

**Continuous Checks (every 5 minutes):**
- ✅ Tier 1 capturing conversations?
- ✅ Events.jsonl growing?
- ✅ Knowledge graph updating?
- ✅ Development context fresh (< 1 hour old)?
- ✅ Hemisphere files updating?
- ✅ Git commits happening?

**Alert Triggers:**
- ❌ No Tier 1 captures in 1 hour
- ❌ No event processing in 2 hours
- ❌ Knowledge graph stale (> 24 hours)
- ❌ Uncommitted work exists for 30+ minutes

**Alert Actions:**
- Write to events.jsonl (dashboard_error)
- Display Windows notification
- Log to monitor-brain-health.log

### 5.2 Add Health Check to Git Hooks

**Update:** `hooks\post-commit`

```bash
# Add after Phase 3:
# ========================================
# PHASE 4: BRAIN Health Validation
# ========================================
echo "🏥 Validating BRAIN health..."
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/monitor-brain-health.ps1 -Quick

if [ $? -ne 0 ]; then
  echo "⚠️  BRAIN health degraded - run full diagnostic"
  echo "   Command: pwsh -File scripts/generate-brain-health-report.ps1"
fi
```

### 5.3 Schedule Periodic Health Checks

**Create:** Windows Task Scheduler entry

```powershell
# File: scripts\setup-brain-health-monitoring.ps1
# Purpose: Create scheduled task for continuous monitoring

$action = New-ScheduledTaskAction -Execute "pwsh.exe" `
    -Argument "-File D:\PROJECTS\KDS\scripts\monitor-brain-health.ps1"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration (New-TimeSpan -Days 365)

Register-ScheduledTask -TaskName "KDS-BRAIN-Health-Monitor" `
    -Action $action -Trigger $trigger
```

---

## Implementation Order (Step-by-Step Execution)

### Day 1 (6-8 hours): Critical Infrastructure

**Morning (4 hours):**
1. ✅ Commit uncommitted work (Phase 1.4)
2. ✅ Create `record-conversation.ps1` (Phase 1.1.1)
3. ✅ Fix auto-recording layers (Phase 1.1.2-1.1.4)
4. ✅ Test conversation capture (validation)

**Afternoon (4 hours):**
5. ✅ Create `analyze-event-patterns.ps1` (Phase 1.2.1)
6. ✅ Lower BRAIN update thresholds (Phase 1.2.3)
7. ✅ Fix development context collection (Phase 1.3)
8. ✅ Test full BRAIN update cycle (validation)

### Day 2 (6-8 hours): Basic Functions

**Morning (4 hours):**
9. ✅ Initialize left hemisphere (Phase 2.1.1)
10. ✅ Update right hemisphere plan (Phase 2.1.2)
11. ✅ Create corpus callosum coordination (Phase 2.1.3)
12. ✅ Test hemisphere sync (validation)

**Afternoon (4 hours):**
13. ✅ Create auto-commit script (Phase 2.2.1)
14. ✅ Activate Brain Protector (Phase 2.3)
15. ✅ Create runtime validator (Phase 2.4)
16. ✅ Test TDD enforcement (validation)

### Day 3 (6-8 hours): Advanced Features + Testing

**Morning (3 hours):**
17. ✅ Implement pattern recognition (Phase 3.1)
18. ✅ Create proactive warnings (Phase 3.2)
19. ✅ Build BRAIN query interface (Phase 3.3)

**Afternoon (5 hours):**
20. ✅ Create stress test scenarios (Phase 4.1)
21. ✅ Build stress test runner (Phase 4.2)
22. ✅ Run all 10 scenarios (Phase 4)
23. ✅ Generate health dashboard (Phase 4.3)
24. ✅ Verify 100% pass rate (validation)

### Day 4 (2-3 hours): Monitoring + Documentation

**Morning (2 hours):**
25. ✅ Create health monitor (Phase 5.1)
26. ✅ Setup scheduled tasks (Phase 5.3)
27. ✅ Run 24-hour soak test (validation)

**Afternoon (1 hour):**
28. ✅ Document BRAIN operations
29. ✅ Create BRAIN user guide
30. ✅ Final verification

---

## Verification Checklist (Definition of DONE)

### Tier 0: Instinct ✅
- [ ] All rules accessible via kds.md
- [ ] Brain Protector enforces TDD, SOLID, DoR/DoD
- [ ] No application data in governance/

### Tier 1: Short-Term Memory ✅
- [ ] Layer 1 (Copilot Chat) auto-imports
- [ ] Layer 2 (Sessions) auto-records on completion
- [ ] Layer 3 (Manual) record-conversation.ps1 works
- [ ] Last 20 conversations preserved
- [ ] FIFO eviction working
- [ ] Conversation capture rate > 90%

### Tier 2: Knowledge Graph ✅
- [ ] Events → Patterns within 1 hour
- [ ] 5+ new patterns from stress test
- [ ] Pattern confidence scores accurate
- [ ] File relationships updated
- [ ] Workflow templates created
- [ ] Correction history tracking

### Tier 3: Development Context ✅
- [ ] Git metrics non-zero and accurate
- [ ] Code changes tracked (lines added/deleted)
- [ ] File hotspots identified
- [ ] Updates every hour automatically
- [ ] Proactive warnings generated

### Tier 4: Event Stream ✅
- [ ] All events logged (coverage > 95%)
- [ ] Event processing < 1 hour lag
- [ ] Pattern extraction working
- [ ] Event integrity validation

### Tier 5: Hemispheres ✅
- [ ] Left: Execution state logged for all tasks
- [ ] Right: Strategic plan updated daily
- [ ] Corpus callosum: Coordination every hour
- [ ] LEFT↔RIGHT misalignment detected
- [ ] Hemisphere specialization maintained

### Automation ✅
- [ ] Git commits after task completion
- [ ] BRAIN updates automatically (events/time)
- [ ] Runtime errors detected pre-commit
- [ ] TDD violations challenged
- [ ] Health monitoring every 5 minutes

### Stress Test ✅
- [ ] 10/10 scenarios pass
- [ ] 100% knowledge retention
- [ ] No amnesia during test
- [ ] All learnings queryable

### Documentation ✅
- [ ] BRAIN operations guide
- [ ] Troubleshooting guide
- [ ] Architecture diagrams
- [ ] API reference (query-brain.ps1)

---

## Rollback Plan (If Restoration Fails)

### Emergency Rollback to Last Known Good State

**If BRAIN restoration causes critical failures:**

```powershell
# 1. Stop all BRAIN processes
Stop-Process -Name "monitor-brain-health" -ErrorAction SilentlyContinue

# 2. Restore from backup
Copy-Item "kds-brain\backups\pre-restoration-*" "kds-brain\" -Recurse -Force

# 3. Restore scripts
git checkout HEAD~1 -- scripts/

# 4. Verify basic functionality
.\scripts\verify-system-health.ps1

# 5. Document failure
# Create: docs/BRAIN-RESTORATION-FAILURE-ANALYSIS.md
```

### Partial Restoration Strategy

**If some phases fail:**
- Keep successful phases active
- Document failed phases
- Create isolated fix for failed component
- Re-test in isolation before integration

---

## Success Metrics

### Before Restoration (Current State)
- Tier 1 Capture Rate: 0% (after 8:10 AM)
- Knowledge Retention: ~5%
- Event Processing Lag: Infinite (not processing)
- Git Commit Automation: 0%
- TDD Enforcement: 0%
- Runtime Error Detection: 0%
- BRAIN Update Frequency: Once per 24+ hours
- Overall BRAIN Health: **5% (CRITICAL)**

### After Restoration (Target)
- Tier 1 Capture Rate: **95%+**
- Knowledge Retention: **100%**
- Event Processing Lag: **< 1 hour**
- Git Commit Automation: **100%**
- TDD Enforcement: **100%** (all violations challenged)
- Runtime Error Detection: **100%** (pre-commit)
- BRAIN Update Frequency: **Every 20 events or 4 hours**
- Overall BRAIN Health: **100% (OPTIMAL)**

### Key Performance Indicators (KPIs)

**Learning Effectiveness:**
- Pattern extraction rate: > 80% of events produce insights
- Knowledge reuse rate: > 50% of tasks benefit from existing patterns
- False positive rate: < 5% (patterns incorrectly applied)

**Automation Effectiveness:**
- Auto-commit success rate: > 95%
- TDD compliance rate: > 90%
- Runtime error catch rate: > 95%

**System Health:**
- BRAIN uptime: > 99.9%
- Health check response time: < 5 seconds
- Recovery time from failure: < 10 minutes

---

## Long-Term Maintenance Plan

### Weekly Tasks
- Review BRAIN health dashboard
- Analyze pattern confidence decay
- Prune low-confidence patterns (< 0.3)
- Verify hemisphere synchronization

### Monthly Tasks
- Run full stress test suite
- Review and update test scenarios
- Analyze knowledge graph growth
- Consolidate duplicate patterns

### Quarterly Tasks
- BRAIN performance audit
- Update threshold tuning
- Review automation effectiveness
- Knowledge graph cleanup (amnesia)

---

## Appendix A: File Inventory

### Files to Create (20 files)
1. `scripts\record-conversation.ps1` - Layer 3 manual recording
2. `scripts\analyze-event-patterns.ps1` - Event → Pattern extraction
3. `scripts\init-left-hemisphere.ps1` - Initialize execution state
4. `scripts\sync-strategic-plan.ps1` - Update right hemisphere from git
5. `scripts\coordinate-brain-hemispheres.ps1` - Corpus callosum coordination
6. `scripts\auto-commit-if-ready.ps1` - Automated git commits
7. `scripts\validate-tdd-before-execution.ps1` - TDD enforcement hook
8. `scripts\validate-runtime-health.ps1` - Runtime error detection
9. `scripts\extract-patterns-from-events.ps1` - Advanced pattern recognition
10. `scripts\generate-proactive-warnings.ps1` - Proactive warning system
11. `scripts\query-brain.ps1` - BRAIN query interface
12. `tests\brain-stress-test-scenarios.yaml` - Test scenarios definition
13. `tests\run-brain-stress-test.ps1` - Test runner
14. `scripts\generate-brain-health-report.ps1` - Health dashboard
15. `scripts\monitor-brain-health.ps1` - Continuous health monitoring
16. `scripts\setup-brain-health-monitoring.ps1` - Scheduled task setup
17. `docs\BRAIN-OPERATIONS-GUIDE.md` - User documentation
18. `docs\BRAIN-TROUBLESHOOTING-GUIDE.md` - Troubleshooting reference
19. `docs\BRAIN-ARCHITECTURE.md` - Architecture diagrams
20. `docs\BRAIN-API-REFERENCE.md` - Query API documentation

### Files to Modify (12 files)
1. `scripts\auto-brain-updater.ps1` - Lower thresholds, add coordination
2. `scripts\brain-updater.ps1` - Add pattern analyzer calls
3. `scripts\collect-development-context.ps1` - Fix metric collection
4. `prompts\internal\code-executor.md` - Add Brain Protector calls
5. `prompts\internal\work-planner.md` - Add TDD validation
6. `prompts\internal\brain-protector.md` - Add runtime error checks
7. `kds-brain\right-hemisphere\active-plan.yaml` - Update current plan
8. `hooks\post-commit` - Add health checks
9. `governance\rules.md` - Add runtime error to DoD
10. `scripts\import-copilot-chats.ps1` - Fix parser (if broken)
11. `scripts\record-session-conversation.ps1` - Fix session detection (if broken)
12. `kds-brain\development-context.yaml` - Populate with real data

### Files to Test (All BRAIN files)
- All 6 tier files (conversation-history.jsonl, knowledge-graph.yaml, development-context.yaml, events.jsonl, execution-state.jsonl, active-plan.yaml)
- All BRAIN scripts (15 scripts)
- All BRAIN agents (6 agents)

---

## Appendix B: Expected Restoration Timeline

### Optimistic (20 hours)
- Day 1: Critical infrastructure (6 hours)
- Day 2: Basic functions (6 hours)
- Day 3: Advanced + testing (6 hours)
- Day 4: Monitoring (2 hours)

### Realistic (28 hours)
- Day 1: Critical infrastructure (8 hours)
- Day 2: Basic functions (8 hours)
- Day 3: Advanced + testing (8 hours)
- Day 4: Monitoring + fixes (4 hours)

### Pessimistic (40 hours)
- Day 1-2: Critical infrastructure (12 hours, debugging)
- Day 3-4: Basic functions (12 hours, integration issues)
- Day 5-6: Advanced + testing (12 hours, scenario failures)
- Day 7: Monitoring + documentation (4 hours)

**Recommendation:** Plan for realistic timeline (28 hours = 3.5 days)

---

## Conclusion

This comprehensive plan addresses ALL failures identified in the BRAIN self-review:

✅ **Git Commits** - Auto-commit after task completion (Phase 2.2)  
✅ **TDD Enforcement** - Brain Protector activation (Phase 2.3)  
✅ **Zero Errors/Warnings** - Runtime validation (Phase 2.4)  
✅ **Tier 1 Capture** - Fix all 3 recording layers (Phase 1.1)  
✅ **Event Processing** - Pattern extraction pipeline (Phase 1.2)  
✅ **Knowledge Transfer** - Automated STM→LTM (Phase 1.2)  
✅ **Hemisphere Coordination** - Corpus callosum activation (Phase 2.1)  
✅ **Development Context** - Fix metric collection (Phase 1.3)  

The plan is **holistic** (all 6 tiers), **verifiable** (stress tests), **forward-thinking** (continuous monitoring), and includes **complete file cleanup** (existing files reviewed and fixed).

**Next Step:** Begin Phase 1.4 (commit uncommitted work) immediately to prevent data loss, then proceed with systematic restoration.

---

**Status:** ✅ PLAN COMPLETE - Ready for execution  
**Author:** GitHub Copilot (BRAIN Restoration Team)  
**Date:** 2025-11-05  
**Version:** 1.0
