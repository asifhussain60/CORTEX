# KDS Workflows - Feature Inventory

**Source System:** KDS v8  
**Target System:** CORTEX v1.0  
**Component:** Core Workflows  
**Date Extracted:** 2025-11-05  
**Status:** Complete Feature List  

---

## 📊 Overview

**Purpose:** Three critical workflows that orchestrate KDS's automated learning and quality enforcement.

**KDS v8 Implementation:**
- Total Workflows: 3 core workflows
- Organization: Event-driven, git-hook triggered, TDD-enforced
- Architecture: Multi-phase, automatic, self-healing
- Location: Distributed across `scripts/`, `hooks/`, agents

**CORTEX v1.0 Design:**
- Workflows: Same 3 workflows preserved
- Architecture: Event-driven + SQLite triggers
- Enhancements: Faster execution, better logging, cross-platform
- Location: `cortex/workflows/`

---

## 📁 Workflow Categories

### 1. TDD Workflow (RED→GREEN→REFACTOR)
**Purpose:** Enforce test-first development for all code changes  
**Phases:** 4 phases (RED, GREEN, REFACTOR, VALIDATE)  
**Duration:** 2-10 minutes per feature  

### 2. Git Commit Workflow
**Purpose:** Automated quality gates + BRAIN learning on every commit  
**Phases:** 4 phases (Health, Tracking, BRAIN Update, Conversation Recording)  
**Duration:** 2-10 seconds per commit  

### 3. BRAIN Update Workflow
**Purpose:** Automatic knowledge graph updates from accumulated events  
**Triggers:** 3 automatic triggers (50 events, 24 hours, session end)  
**Duration:** 2-60 seconds (Tier 2), 2-5 minutes (Tier 2+3)  

---

## 🔴 Workflow 1: TDD Workflow (RED→GREEN→REFACTOR)

### Overview

**Purpose:** Enforce test-first development (RED→GREEN→REFACTOR cycle) for all production code changes.

**Philosophy:**
> "Tests are the specification. Write the specification before writing the implementation."

**Enforcement:** 
- Tier 0 Rule #5 (TEST_FIRST_TDD - CRITICAL severity)
- Git pre-commit hook validation
- Code Executor agent integration

**Success Rate:** 95%+ TDD compliance in KDS v8

---

### Phase 1: RED - Write Failing Tests

**Objective:** Create tests that define expected behavior BEFORE implementation exists.

**Workflow:**
```
1. Parse feature requirements → Test cases
2. Create test file(s) with failing tests
3. Run tests → Verify they FAIL
4. Commit RED state (optional, for tracking)
5. Log RED phase to execution-state.jsonl
```

**Automation Script:** `scripts/left-brain/create-tests.ps1`

**Features:**
```powershell
Input:
  - Feature config YAML (feature_name, tests_to_create)
  - Test framework type (Playwright, xUnit, Jest, pytest)
  - Expected behavior description

Process:
  - Generate test file structure
  - Create test methods with assertions
  - Add test data/fixtures
  - Format code (Prettier/EditorConfig)

Output:
  - Test file paths created
  - Test count
  - Expected: ALL TESTS FAIL (no implementation yet)

Verification:
  - Run tests via execute-tests.ps1
  - Verify exit code != 0 (failure expected)
  - Log RED phase event
```

**Example Test (Playwright):**
```typescript
// Created in RED phase - EXPECTED TO FAIL
test('export to PDF button visible on dashboard', async ({ page }) => {
  await page.goto('/dashboard');
  
  const exportButton = page.getByTestId('export-pdf-btn');
  await expect(exportButton).toBeVisible();  // ❌ FAILS - button doesn't exist yet
});
```

**CORTEX Migration:**
- Python `TestCreator` class
- Jinja2 templates for test generation
- Framework detection (Playwright, pytest, unittest)
- AST-based test structure validation

---

### Phase 2: GREEN - Implement Minimum Code

**Objective:** Write MINIMUM code needed to make tests pass (no more, no less).

**Workflow:**
```
1. Create implementation file(s)
2. Implement minimal code to satisfy tests
3. Run tests → Verify they PASS
4. Commit GREEN state
5. Log GREEN phase to execution-state.jsonl
```

**Automation Script:** `scripts/left-brain/implement-code.ps1`

**Features:**
```powershell
Input:
  - Feature config YAML (files_to_create, implementation_details)
  - Test file paths (from RED phase)
  - Implementation template (optional)

Process:
  - Create implementation file(s)
  - Add minimal code (methods, classes, components)
  - Run tests to verify GREEN
  - Automatic rollback if tests fail

Output:
  - Implementation file paths
  - Test results (must be ALL PASS)
  - Lines of code added

Verification:
  - Run tests via execute-tests.ps1
  - Verify exit code == 0 (all pass)
  - Log GREEN phase event
  
Rollback:
  - If tests fail → rollback-changes.ps1
  - Git reset to last known good state
  - Log rollback event
```

**Example Implementation (C#):**
```csharp
// Created in GREEN phase - MINIMAL to make test pass
public class DashboardController
{
    public IActionResult Index()
    {
        // MINIMAL: Just add the button to view
        ViewBag.ShowExportPdf = true;  // ✅ Makes test pass
        return View();
    }
}
```

**CORTEX Migration:**
- Python `CodeImplementer` class
- AST-based code generation
- Syntax validation before commit
- Automatic test execution

---

### Phase 3: REFACTOR - Optimize Code

**Objective:** Improve code quality (DRY, SOLID, clarity) while keeping tests GREEN.

**Workflow:**
```
1. Identify refactoring opportunities
2. Apply refactoring patterns (extract method, rename, etc.)
3. Run tests → Verify they STILL PASS
4. Commit REFACTOR state
5. Log REFACTOR phase to execution-state.jsonl
```

**Automation Script:** `scripts/left-brain/refactor-code.ps1`

**Features:**
```powershell
Input:
  - Implementation file path(s)
  - Refactoring patterns to apply
  - Test file paths (for verification)

Refactoring Patterns:
  - Extract method (long methods → smaller)
  - Rename (unclear names → clear)
  - Remove duplication (DRY principle)
  - Extract constant/variable
  - Simplify conditionals

Process:
  - Apply refactoring transformation
  - Run tests to verify still GREEN
  - Automatic rollback if tests break

Output:
  - Refactored code
  - Test results (must be ALL PASS)
  - Refactoring type applied

Verification:
  - Run tests via execute-tests.ps1
  - Verify exit code == 0 (still passing)
  - Log REFACTOR phase event

Safety Net:
  - If tests fail → rollback-changes.ps1
  - Rollback to GREEN state
  - Log safety net triggered
```

**Example Refactor (C#):**
```csharp
// REFACTOR phase - Improved code while tests stay green
public class DashboardController
{
    private readonly IPdfExportService _pdfService;  // Dependency injection added
    
    public DashboardController(IPdfExportService pdfService)
    {
        _pdfService = pdfService ?? throw new ArgumentNullException(nameof(pdfService));
    }
    
    public IActionResult Index()
    {
        var model = new DashboardViewModel
        {
            ExportToPdfEnabled = _pdfService.IsAvailable()  // Better abstraction
        };
        return View(model);
    }
}
// ✅ Tests still pass, code quality improved
```

**CORTEX Migration:**
- Python `CodeRefactorer` class
- Automated refactoring patterns (rope library)
- Safety checks (tests must stay green)
- Pattern library for common refactors

---

### Phase 4: VALIDATE - Definition of Done

**Objective:** Verify all quality gates pass before marking feature complete.

**Workflow:**
```
1. Run all tests → ALL PASS
2. Build project → 0 errors, 0 warnings
3. Run linters/analyzers → 0 violations
4. Verify TDD compliance → Documented
5. Health check → System stable
```

**Automation Script:** `scripts/left-brain/validate-implementation.ps1`

**Features:**
```powershell
Quality Gates:
  ✅ All tests passing (unit, integration, E2E)
  ✅ Build successful (dotnet build, npm build)
  ✅ Zero errors
  ✅ Zero warnings (StyleCop, ESLint, etc.)
  ✅ Code coverage >= 80% (for new code)
  ✅ TDD cycle documented (RED→GREEN→REFACTOR)

Checks:
  - Test results (from execute-tests.ps1)
  - Build output (dotnet build --no-restore)
  - Linter results (eslint, prettier, stylelint)
  - Analyzer results (Roslyn analyzers, StyleCop)
  - Coverage report (dotnet test --collect:"XPlat Code Coverage")

Output:
  - Validation status (PASS/FAIL)
  - Gate results (which gates passed/failed)
  - Recommendations (if validation failed)

Enforcement:
  - Pre-commit hook checks validation
  - Commit BLOCKED if validation fails
  - Manual override possible (with warning logged)
```

**CORTEX Migration:**
- Python `ValidationOrchestrator` class
- Plugin architecture for validation checks
- Fast validation (<5 seconds)
- Parallel check execution

---

### TDD Orchestrator (Master Script)

**File:** `scripts/left-brain/run-tdd-cycle.ps1` (~217 lines)

**Purpose:** Coordinate complete RED→GREEN→REFACTOR→VALIDATE cycle automatically.

**Features:**
```powershell
Input:
  - Feature config YAML path
  - Dry run flag (optional)
  - Verbose logging (optional)

Orchestration:
  Phase 1: RED
    → create-tests.ps1
    → verify-red-phase.ps1
    → Log RED event
    
  Phase 2: GREEN
    → implement-code.ps1
    → verify-green-phase.ps1
    → If FAIL: rollback-changes.ps1
    → Log GREEN event
    
  Phase 3: REFACTOR
    → refactor-code.ps1
    → verify-refactor-safety.ps1
    → If FAIL: rollback-changes.ps1
    → Log REFACTOR event
    
  Phase 4: VALIDATE
    → validate-implementation.ps1
    → If FAIL: Report issues
    → Log VALIDATE event

Output:
  - Success/failure status
  - Phase durations
  - Files created/modified
  - Test results
  - Validation results

Execution State Logging:
  - All phases logged to kds-brain/left-hemisphere/execution-state.jsonl
  - RIGHT brain analyzes for optimization
  - Corpus Callosum processes feedback
```

**Usage:**
```powershell
# Automatic TDD cycle for a feature
.\scripts\left-brain\run-tdd-cycle.ps1 `
    -FeatureConfig "tests\fixtures\tdd-cycle\pdf-export-feature.yaml" `
    -Verbose

# Dry run (preview phases)
.\scripts\left-brain\run-tdd-cycle.ps1 `
    -FeatureConfig "feature.yaml" `
    -DryRun
```

**CORTEX Migration:**
- Python `TDDOrchestrator` class
- Async phase execution
- Real-time progress reporting (tqdm)
- SQLite state tracking

---

### TDD Workflow Summary

| Phase | Script | Duration | Outcome | Rollback |
|-------|--------|----------|---------|----------|
| **RED** | `create-tests.ps1` | 30-60s | Tests FAIL | N/A |
| **GREEN** | `implement-code.ps1` | 2-5 min | Tests PASS | Yes |
| **REFACTOR** | `refactor-code.ps1` | 1-3 min | Tests PASS | Yes |
| **VALIDATE** | `validate-implementation.ps1` | 10-30s | All gates PASS | N/A |
| **Total** | `run-tdd-cycle.ps1` | **4-10 min** | **Feature complete** | **Automatic** |

---

## 🔄 Workflow 2: Git Commit Workflow

### Overview

**Purpose:** Automated quality enforcement + BRAIN learning triggered by every git commit.

**Philosophy:**
> "Every commit is a learning opportunity. Capture context, validate quality, feed the BRAIN."

**Trigger:** Git `post-commit` hook (automatic, <10 seconds)

**Hooks:**
- `hooks/post-commit` (4 phases)
- `hooks/pre-commit` (quality gates)
- `hooks/post-merge` (BRAIN refresh)

**Version:** 8.0 (V8 Enhancement: Git commit → conversation tracking)

---

### Pre-Commit Hook (Quality Gates)

**File:** `hooks/pre-commit` (~100 lines bash)

**Purpose:** Prevent bad commits BEFORE they enter git history.

**Checks:**
```bash
1. Repository Validation
   - Verify in KDS repository (not DevProjects)
   - Prevent accidental commits to wrong repo
   - Exit 1 if wrong repo

2. Commit Message Convention
   - Format: <type>(kds): <description>
   - Types: feat|fix|docs|chore|refactor|test|style|perf|ci|build|revert
   - Example: "feat(kds): Add PDF export to dashboard"
   - Warn if non-compliant (allow override)

3. Sensitive Files Check
   - Block .env, .key, .secret, .password, .token files
   - Prevent credential leaks
   - Exit 1 if sensitive files staged

4. BRAIN YAML Validation
   - Validate all kds-brain/*.yaml files
   - Check YAML syntax (Python yaml.safe_load)
   - Exit 1 if invalid YAML

5. Tier 0 Enforcement (PowerShell)
   - Call scripts/validate-commit.ps1
   - Check TDD compliance
   - Check Definition of Done
   - Check zero errors/warnings
   - Exit 1 if validation fails
```

**Example Pre-Commit Check:**
```bash
🔍 KDS Pre-Commit Hook - Validating commit...
  ✅ Repository validated: KDS
  ✅ Commit message validated
  ✅ No sensitive files
  ✅ BRAIN YAML files valid
  
  Running Tier 0 Enforcement...
  ✅ TDD compliance verified
  ✅ Build: 0 errors, 0 warnings
  ✅ All tests passing

✅ All pre-commit validations passed
```

**CORTEX Migration:**
- Python-based pre-commit hook
- Configurable quality gates
- Fast validation (<5 seconds)

---

### Post-Commit Hook (Learning & Tracking)

**File:** `hooks/post-commit` (~80 lines bash)

**Purpose:** Automatic BRAIN learning + health monitoring after every commit.

**Phases:**

#### Phase 1: Critical Health Checks (<2s)

**Script:** `scripts/health-check-critical.ps1`

**Checks:**
```powershell
Fast Validations:
  - BRAIN files exist (events.jsonl, knowledge-graph.yaml, etc.)
  - Event log writable
  - Git repository healthy
  - Critical directories present

Performance:
  - Target: <2 seconds
  - 18ms average in KDS v8
  - Silent mode (no output unless error)

Output:
  - Exit code 0: All healthy
  - Exit code 1: Health issue detected
  - Warning displayed (commit proceeds anyway)
```

**Example:**
```bash
🔍 Running critical health checks...
  ✅ Health check passed (18ms)
```

---

#### Phase 2: Git Commit → Conversation Tracking (V8 NEW)

**Script:** `scripts/associate-commit-to-conversation.ps1`

**Purpose:** Associate git commits with active Copilot conversations for full traceability.

**Features:**
```powershell
Process:
  1. Get current git commit hash
  2. Find active conversation in Tier 1 (conversation-context.jsonl)
  3. Associate commit with conversation
  4. Update conversation metadata
  5. Log association event

Data Captured:
  - Commit hash
  - Commit message
  - Files changed
  - Author
  - Timestamp
  - Associated conversation ID

Storage:
  - conversation-context.jsonl (metadata)
  - events.jsonl (association event)

Benefits:
  - Full audit trail (conversation → commits)
  - Resume conversation with commit context
  - Track feature implementation progress
```

**Example Association:**
```json
{
  "conversation_id": "20251105-pdf-export",
  "commits": [
    {
      "hash": "a1b2c3d",
      "message": "feat(kds): Add PDF export to dashboard",
      "files": ["DashboardController.cs", "PdfService.cs"],
      "timestamp": "2025-11-05T10:30:00Z"
    }
  ]
}
```

**CORTEX Migration:**
- SQLite conversation-commit association table
- Real-time tracking
- Query: "Show me all commits from conversation X"

---

#### Phase 3: Auto BRAIN Update

**Script:** `scripts/auto-brain-updater.ps1`

**Purpose:** Trigger BRAIN update if thresholds met (see Workflow 3 for details).

**Process:**
```powershell
1. Log commit event to events.jsonl
   - Event type: "git_commit"
   - Commit message
   - Files changed
   - Agent: "git-commit"

2. Check BRAIN update thresholds
   - Count unprocessed events
   - Check hours since last update
   
3. IF threshold met → Trigger BRAIN update
   - Event threshold: 50+ events
   - Time threshold: 24 hours + 10 events
   
4. Throttle Tier 3 collection
   - Only if last collection > 1 hour
   - Avoid expensive operations
```

**Example:**
```bash
🧠 Auto BRAIN Update Check...
📊 Events: 52 (threshold: 50)
⏰ Hours since update: 2.3 (threshold: 24)

✅ Event threshold met - triggering BRAIN update
   ⏱️  Updating Tier 2 (knowledge graph)... 3s
   ⏭️  Tier 3 skipped (last collection 15 min ago)
   ✅ BRAIN updated successfully
```

**CORTEX Migration:**
- Python `AutoBrainUpdater` class
- Event-driven triggers
- SQLite event counting

---

#### Phase 4: Tier 1 Auto-Recording

**Purpose:** Automatically capture conversations from multiple sources.

**Layer 1: Copilot Chat Detection**

**Script:** `scripts/import-copilot-chats.ps1`

**Trigger:**
```bash
# If commit includes .github/workflows/CopilotChats.txt
if git diff-tree -r --name-only --no-commit-id HEAD | grep -q "CopilotChats.txt"; then
  pwsh -File scripts/import-copilot-chats.ps1
fi
```

**Process:**
```powershell
1. Detect CopilotChats.txt in commit
2. Parse chat export format
3. Extract conversation metadata
4. Store in conversation-history.jsonl
5. Update conversation-context.jsonl
```

---

**Layer 2: Session Completion Detection**

**Script:** `scripts/record-session-conversation.ps1`

**Trigger:**
```bash
# If commit includes sessions/*.json files
SESSION_FILES=$(git diff-tree -r --name-only --no-commit-id HEAD | grep "sessions/.*\.json")
for SESSION_FILE in $SESSION_FILES; do
  pwsh -File scripts/record-session-conversation.ps1 -SessionFile "$SESSION_FILE"
done
```

**Process:**
```powershell
1. Detect session file changes
2. Parse session JSON
3. Extract conversation summary
4. Store in conversation-history.jsonl
5. Mark session as recorded
```

---

### Post-Merge Hook (BRAIN Refresh)

**File:** `hooks/post-merge` (similar to post-commit)

**Purpose:** Full BRAIN refresh after merging branches.

**Process:**
```bash
1. Full health check (not just critical)
2. Force BRAIN update (bypass thresholds)
3. Refresh all tiers
4. Repository sync validation
```

**CORTEX Migration:**
- Python-based hooks
- SQLite BRAIN state sync
- Conflict resolution

---

### Git Commit Workflow Summary

| Phase | Script | Duration | Purpose |
|-------|--------|----------|---------|
| **Pre-Commit** | `validate-commit.ps1` | 2-5s | Quality gates |
| **Post Phase 1** | `health-check-critical.ps1` | <2s | Health validation |
| **Post Phase 2** | `associate-commit-to-conversation.ps1` | <1s | Git→conversation link |
| **Post Phase 3** | `auto-brain-updater.ps1` | 0-60s | BRAIN learning |
| **Post Phase 4** | `import-copilot-chats.ps1` | <2s | Tier 1 recording |
| **Total** | **All hooks** | **4-10s** | **Quality + Learning** |

---

## 🧠 Workflow 3: BRAIN Update Workflow

### Overview

**Purpose:** Automatic knowledge graph updates from accumulated interaction events.

**Philosophy:**
> "The BRAIN learns continuously. Events accumulate, patterns emerge, knowledge grows."

**Triggers:** 3 automatic + 1 manual

**Agent:** `brain-updater.md` (RIGHT BRAIN - Strategic)

**Tiers Updated:**
- Tier 2: Knowledge Graph (always)
- Tier 3: Development Context (throttled, >1 hour)

---

### Trigger 1: Event Threshold (50+ Events)

**Condition:** 50 or more unprocessed events in `kds-brain/events.jsonl`

**Rationale:**
- 50 events = significant interaction volume
- Patterns likely emerged
- Knowledge graph needs update

**Check:**
```powershell
# Count events since last BRAIN update
$lastUpdate = (Get-Item "kds-brain\knowledge-graph.yaml").LastWriteTime
$eventsSince = Get-Content "kds-brain\events.jsonl" | 
    ConvertFrom-Json | 
    Where-Object { [DateTime]$_.timestamp -gt $lastUpdate } | 
    Measure-Object | 
    Select-Object -ExpandProperty Count

if ($eventsSince -ge 50) {
    # TRIGGER BRAIN UPDATE
}
```

**Automatic Trigger Points:**
- Git post-commit hook (after every commit)
- Agent task completion (after agent work)
- End of session (when session marked complete)

**Example:**
```bash
📊 Events: 52 (threshold: 50)
✅ Event threshold met - triggering BRAIN update
```

---

### Trigger 2: Time Threshold (24 Hours + 10 Events)

**Condition:** 24+ hours since last update AND 10+ unprocessed events

**Rationale:**
- Prevent stale knowledge graph (even with low activity)
- 10 events minimum (avoid update for trivial activity)
- Daily refresh ensures BRAIN stays current

**Check:**
```powershell
$lastUpdate = (Get-Item "kds-brain\knowledge-graph.yaml").LastWriteTime
$hoursSince = ((Get-Date) - $lastUpdate).TotalHours
$eventCount = (Get-Content "kds-brain\events.jsonl" | Measure-Object).Count

if ($hoursSince -ge 24 -and $eventCount -ge 10) {
    # TRIGGER BRAIN UPDATE
}
```

**Example:**
```bash
⏰ Hours since update: 26.3 (threshold: 24)
📊 Events: 15 (minimum: 10)
✅ Time threshold met - triggering BRAIN update
```

---

### Trigger 3: Session Completion

**Condition:** All tasks in session marked as complete

**Rationale:**
- Session represents complete work unit
- Capture learnings before context lost
- Pattern extraction while fresh

**Implementation:**
```powershell
# When session marked complete
$session = Get-Content "sessions\$sessionId.json" | ConvertFrom-Json
if ($session.status -eq "complete") {
    # TRIGGER BRAIN UPDATE
    Invoke-BrainUpdater -SessionId $sessionId
}
```

**Example:**
```bash
✅ Session complete: "Add PDF export to dashboard"
🧠 Triggering BRAIN update to capture learnings
```

---

### Trigger 4: Manual Invocation

**Condition:** User explicitly requests BRAIN update

**Usage:**
```markdown
#file:KDS/prompts/internal/brain-updater.md

Update the BRAIN with all new events
```

**Use Cases:**
- Immediate pattern extraction needed
- Troubleshooting BRAIN state
- Force refresh after major changes

---

### BRAIN Update Process

#### Step 1: Event Collection & Parsing

**Input:** `kds-brain/events.jsonl`

**Process:**
```powershell
1. Read all events since last update
2. Parse event types:
   - test_created
   - implementation_complete
   - validation_passed
   - commit_created
   - pattern_detected
   - error_encountered
   - rollback_triggered

3. Group events by:
   - Agent (who)
   - Intent (what)
   - Outcome (success/fail)
   - Timestamp (when)
   - Files affected (where)
```

**Example Events:**
```jsonl
{"timestamp":"2025-11-05T10:15:00Z","event":"test_created","agent":"test-generator","files":["PdfServiceTests.cs"],"outcome":"success"}
{"timestamp":"2025-11-05T10:20:00Z","event":"implementation_complete","agent":"code-executor","files":["PdfService.cs"],"outcome":"success"}
{"timestamp":"2025-11-05T10:22:00Z","event":"validation_passed","agent":"health-validator","outcome":"success"}
{"timestamp":"2025-11-05T10:25:00Z","event":"commit_created","agent":"commit-handler","message":"feat(kds): Add PDF export","outcome":"success"}
```

---

#### Step 2: Pattern Extraction

**Purpose:** Identify reusable patterns from event sequences.

**Pattern Types:**

1. **Workflow Patterns** (Event sequences)
```yaml
pattern_id: pdf_export_workflow
pattern_type: workflow
confidence: 0.95
events:
  - test_created → implementation_complete → validation_passed → commit_created
success_rate: 100%
duration: 10 minutes
```

2. **Error Patterns** (Failure sequences)
```yaml
pattern_id: test_failure_rollback
pattern_type: error_recovery
confidence: 0.88
events:
  - implementation_complete → validation_failed → rollback_triggered
recovery_time: 30 seconds
```

3. **Agent Collaboration Patterns**
```yaml
pattern_id: tdd_collaboration
pattern_type: agent_coordination
agents: [test-generator, code-executor, health-validator]
message_flow: RIGHT → LEFT → LEFT
success_rate: 98%
```

---

#### Step 3: Knowledge Graph Update

**File:** `kds-brain/knowledge-graph.yaml`

**Updates:**

1. **Add New Patterns**
```yaml
patterns:
  pdf_export_workflow:
    type: feature_implementation
    phases: 4
    duration: 10 min
    success_rate: 100%
    first_seen: 2025-11-05
    last_used: 2025-11-05
    usage_count: 1
```

2. **Update Existing Patterns**
```yaml
patterns:
  tdd_cycle:
    usage_count: 47  # Incremented
    last_used: 2025-11-05  # Updated
    success_rate: 0.98  # Recalculated
    avg_duration: 8.5 min  # Recalculated
```

3. **Increment Version**
```yaml
version: 8.15  # Was 8.14
last_updated: 2025-11-05T10:30:00Z
```

---

#### Step 4: Tier 3 Collection (Throttled)

**Condition:** Last Tier 3 collection > 1 hour ago

**Purpose:** Update development context metrics (git, test, build, work patterns).

**Script:** `scripts/collect-development-context.ps1`

**Metrics Collected:**

1. **Git Activity**
```yaml
git_activity:
  commits_today: 12
  commit_velocity: 0.8 per hour
  churn_rate: 150 lines/commit
  active_branches: 3
```

2. **Code Health**
```yaml
code_health:
  build_status: passing
  warnings: 0
  errors: 0
  test_pass_rate: 100%
```

3. **Testing Metrics**
```yaml
testing:
  total_tests: 347
  tests_added_today: 15
  flaky_tests: 0
  coverage: 87%
```

4. **KDS Usage**
```yaml
kds_usage:
  intents_today: 18
  top_intent: CODE_IMPLEMENTATION
  avg_response_time: 45 seconds
```

**Performance:**
- Collection time: 2-5 minutes
- Throttling: Max 1x per hour
- Efficiency: 75% reduction in Tier 3 overhead

---

#### Step 5: Event Archival

**Process:**
```powershell
1. Mark processed events
   - Add "processed": true field
   - Add "processed_at": timestamp

2. Archive old events (optional)
   - Move events >30 days to archive
   - Keep events.jsonl manageable

3. Reset event counter
   - Clear "unprocessed" count
```

---

### BRAIN Update Workflow Summary

| Step | Process | Duration | Output |
|------|---------|----------|--------|
| **1. Collect** | Parse events.jsonl | 1-2s | Event list |
| **2. Extract** | Identify patterns | 2-5s | Pattern objects |
| **3. Update KG** | Update knowledge-graph.yaml | 2-5s | Updated KG |
| **4. Tier 3** | Collect dev context (throttled) | 0-300s | Updated context |
| **5. Archive** | Mark events processed | 1-2s | Clean events log |
| **Total** | **Tier 2 only** | **5-15s** | **BRAIN updated** |
| **Total** | **Tier 2 + 3** | **2-5 min** | **Full refresh** |

---

### Auto-Brain-Updater Script

**File:** `scripts/auto-brain-updater.ps1` (~300 lines)

**Parameters:**
```powershell
-RequestSummary    # Brief summary of request (for event logging)
-ResponseType      # agent|direct|error
-AgentInvoked      # Name of agent invoked (if any)
-Silent            # Suppress output (for background execution)
```

**Features:**

1. **Event Logging**
```powershell
# Log request as event
$event = @{
    timestamp = (Get-Date -Format "o")
    event = "copilot_request"
    request_summary = $RequestSummary
    response_type = $ResponseType
    agent_invoked = $AgentInvoked
} | ConvertTo-Json -Compress

Add-Content "kds-brain\events.jsonl" $event
```

2. **Threshold Checking**
```powershell
$eventCount = (Get-Content "kds-brain\events.jsonl" | Measure-Object).Count
$lastUpdate = (Get-Item "kds-brain\knowledge-graph.yaml").LastWriteTime
$hoursSince = ((Get-Date) - $lastUpdate).TotalHours

$eventThresholdMet = $eventCount -ge 50
$timeThresholdMet = $hoursSince -ge 24 -and $eventCount -ge 10
```

3. **Script Sync**
```powershell
# Keep brain-updater.ps1 in sync with brain-updater.md
if ((Get-Item "prompts\internal\brain-updater.md").LastWriteTime -gt 
    (Get-Item "scripts\brain-updater.ps1").LastWriteTime) {
    
    # Regenerate script from agent definition
    Convert-Agent-To-Script -AgentFile "brain-updater.md"
}
```

4. **BRAIN Update Invocation**
```powershell
if ($eventThresholdMet -or $timeThresholdMet) {
    # Invoke brain-updater agent
    & "scripts\brain-updater.ps1"
}
```

**CORTEX Migration:**
- Python `AutoBrainUpdater` class
- Scheduled task (cron/systemd)
- SQLite event counting
- Real-time triggers

---

## 📊 Workflow Integration

### How Workflows Interact

```
User Request → Intent Router
                ↓
         Work Planner → TDD Workflow (Workflow 1)
                         ↓
                   Code Executor (RED→GREEN→REFACTOR)
                         ↓
                   Health Validator (VALIDATE)
                         ↓
                   Commit Handler → Git Commit (Workflow 2)
                                     ↓
                              Post-Commit Hook
                                     ↓
                              Phase 1: Health Check
                              Phase 2: Conversation Tracking
                              Phase 3: Auto BRAIN Update (Workflow 3)
                              Phase 4: Tier 1 Recording
                                     ↓
                              BRAIN Updated → Next Request Smarter
```

---

### Workflow Metrics (KDS v8)

| Workflow | Avg Duration | Success Rate | Daily Executions |
|----------|--------------|--------------|------------------|
| **TDD** | 6 minutes | 95% | 8-12 |
| **Git Commit** | 5 seconds | 100% | 12-20 |
| **BRAIN Update** | 10 seconds | 98% | 2-4 |

---

## 🎯 CORTEX Migration Strategy

### 1. Workflow Preservation

**Keep:**
- ✅ TDD RED→GREEN→REFACTOR→VALIDATE phases
- ✅ Git hook triggers (pre-commit, post-commit, post-merge)
- ✅ BRAIN update thresholds (50 events, 24 hours, session end)
- ✅ Multi-layer conversation recording
- ✅ Automatic rollback on test failure

**Enhance:**
- ⚡ Faster execution (Python > PowerShell)
- ⚡ Better logging (structured SQLite logs)
- ⚡ Cross-platform (Linux/Mac support)
- ⚡ Real-time progress (tqdm, rich)

---

### 2. Language Migration

**PowerShell → Python:**

| Component | KDS v8 | CORTEX v1.0 |
|-----------|--------|-------------|
| TDD Orchestrator | `run-tdd-cycle.ps1` | `TDDOrchestrator.py` |
| Git Hooks | Bash + PowerShell | Python + pre-commit framework |
| BRAIN Updater | `auto-brain-updater.ps1` | `AutoBrainUpdater.py` |
| Event Logging | JSONL files | SQLite + JSONL backup |

---

### 3. Performance Targets

| Metric | KDS v8 | CORTEX Target | Improvement |
|--------|--------|---------------|-------------|
| TDD Cycle | 6 min | 4 min | 33% faster |
| Git Commit Hook | 5 sec | 3 sec | 40% faster |
| BRAIN Update (Tier 2) | 10 sec | 5 sec | 50% faster |
| BRAIN Update (Tier 2+3) | 3 min | 2 min | 33% faster |

---

### 4. Testing Strategy

**Unit Tests:**
- TDD orchestrator (50+ tests)
- Git hook integration (30+ tests)
- BRAIN update logic (40+ tests)

**Integration Tests:**
- Full TDD cycle (end-to-end)
- Git commit workflow (all 4 phases)
- BRAIN update workflow (all 5 steps)

**Performance Tests:**
- TDD cycle <4 minutes
- Git hooks <3 seconds
- BRAIN update <5 seconds (Tier 2)

---

## ✅ Migration Checklist

### TDD Workflow
- [ ] Convert PowerShell scripts to Python
- [ ] Create `TDDOrchestrator` class
- [ ] Implement RED/GREEN/REFACTOR phases
- [ ] Add automatic rollback
- [ ] Add validation phase
- [ ] Write 50+ unit tests
- [ ] Performance test (<4 min target)

### Git Commit Workflow
- [ ] Migrate git hooks to Python
- [ ] Implement pre-commit validation
- [ ] Implement post-commit phases (4)
- [ ] Add conversation tracking
- [ ] Add BRAIN update trigger
- [ ] Write 30+ integration tests
- [ ] Performance test (<3 sec target)

### BRAIN Update Workflow
- [ ] Convert auto-brain-updater to Python
- [ ] Implement event collection
- [ ] Implement pattern extraction
- [ ] Implement knowledge graph update
- [ ] Implement Tier 3 throttling
- [ ] Write 40+ unit tests
- [ ] Performance test (<5 sec Tier 2)

### Validation
- [ ] Full TDD cycle works end-to-end
- [ ] Git hooks trigger correctly
- [ ] BRAIN updates automatically
- [ ] Rollback safety net functional
- [ ] Cross-platform compatibility

---

## ✅ Completion Status

**Workflows Inventory:** ✅ COMPLETE  
**Total Workflows:** 3 core workflows  
**Total Features:** 50+ features across all workflows  
**CORTEX Enhancement:** 30-40% faster execution + cross-platform  

**Next Steps:**
1. Update PROGRESS.md to mark Workflows inventory complete
2. Continue with Dashboard inventory (final component)
3. Begin Phase 0 implementation after inventory complete

---

**Extracted By:** GitHub Copilot  
**Date:** 2025-11-05  
**Source:** KDS v8 workflows (TDD, Git Commit, BRAIN Update)  
**Status:** ✅ Complete and comprehensive
