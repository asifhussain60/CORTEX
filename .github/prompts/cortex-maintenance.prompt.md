---
mode: agent
description: "CORTEX System Maintenance - Automated health checks, auto-repair, and system optimization"
---

# 🩺 CORTEX System Maintenance

**Purpose:** Automatically diagnose AND repair CORTEX system issues to maintain peak performance. This is NOT a diagnostic-only tool - it FIXES problems automatically.

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 Core Philosophy

**MAINTENANCE = DIAGNOSE + AUTO-REPAIR + VERIFY**

| Phase | Action | Automation Level |
|-------|--------|------------------|
| **DIAGNOSE** | Identify gaps, errors, unwired components | ✅ Fully Automated |
| **AUTO-REPAIR** | Patch source code, wire components, fix issues | ✅ Fully Automated |
| **VERIFY** | Confirm 100% health, run tests, validate fixes | ✅ Fully Automated |

**⚠️ CRITICAL:** If maintenance only identifies problems but doesn't fix them, it's a BUG in the maintenance system itself.

---

## 🚨 Enforcement Rules

### Rule 1: AUTO-REPAIR is MANDATORY

**❌ FORBIDDEN:**
- Generating reports without fixing issues
- Leaving wiring gaps after maintenance completes
- Requiring manual intervention for known issues
- Outputting "TODO: Fix manually" messages

**✅ REQUIRED:**
- Every detected issue has an auto-repair handler
- 100% wiring coverage achieved automatically
- All tests passing (100%) after maintenance
- Source code committed with fixes

### Rule 2: Idempotency

Running maintenance twice on the same system should:
- ✅ Produce identical results (no changes second time)
- ✅ Report "All systems healthy" if no issues
- ✅ Not break previously working components

### Rule 3: Persistence

Maintenance fixes MUST:
- ✅ Modify source code (not just configs)
- ✅ Be git-committable
- ✅ Persist across `git pull` operations
- ✅ Work on all machines without re-running maintenance

**Reference:** `cortex-brain/documents/analysis/maintenance-wiring-persistence-gap.md`

---

## Phase 1.5: Interactive Workflow Wiring Validation 🔄 NEW

**Purpose:** Ensure orchestrators with interactive capabilities have complete wiring from decision logic through user interface.

**Reference:** `cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md`

**Critical:** Interactive components built but not wired = technical debt + broken user experience.

### 1.5a. Identify Interactive Orchestrators

Orchestrators that SHOULD support interactive mode:

| Orchestrator | Status | Interactive Components | Wired? |
|--------------|--------|----------------------|--------|
| **Planning** | Built | `interactive_session.py` (648 LOC) | ❌ No |
| **ADO** | Not Built | Should have `interactive_ado_session.py` | ❌ No |
| **Maintenance** | Future | TBD | ⏸️ Deferred |
| **Sanitization** | Future | TBD | ⏸️ Deferred |

### 1.5b. Universal Wiring Checklist + AUTO-REPAIR

For EACH orchestrator with interactive mode, verify AND FIX all 6 components:

#### Component 1: Decision Logic ✅

**File:** `src/orchestrators/{name}/{name}_orchestrator.py`

**Required Method:**
```python
def _should_use_interactive_mode(self, kwargs: Dict) -> bool:
    """
    Decide if interactive mode is needed.
    
    Criteria:
    - Explicit request: kwargs.get("interactive", False)
    - User preference: config.get("prefer_interactive", False)
    - Complexity: Tier 4 (complex operations)
    - Confidence: Low (<60%)
    - Conflicts: Existing artifact detected
    """
    pass
```

**Validation Commands:**
```bash
# Check if method exists
grep -n "_should_use_interactive_mode" src/orchestrators/planning/planning_orchestrator.py

# Check if method is CALLED in execute()
grep -A 3 "_should_use_interactive_mode" src/orchestrators/planning/planning_orchestrator.py
```

**Expected:** Method exists AND is called before generation phase.

**❌ IF MISSING → AUTO-REPAIR:**
```python
# If method not called in execute(), patch it automatically
# See Phase 4a for auto_wire_orchestrators.py implementation
```

---

#### Component 2: Agent Registration ✅

**File:** `src/cortex_agents/agent_registry.py`

**Required Registration:**
```python
AGENT_REGISTRY = {
    "planning": PlanningAgent,
    "review": ReviewAgent,
    "interactive_planning": InteractivePlanner,  # ← Must exist
    "interactive_ado": InteractiveADOPlanner,    # ← Must exist
}
```

**Validation Commands:**
```bash
# Check agent registry
grep "interactive_planning" src/cortex_agents/agent_registry.py
grep "interactive_ado" src/cortex_agents/agent_registry.py

# Check agent imports
grep "from.*interactive_planner import" src/cortex_agents/agent_registry.py
```

**Expected:** All interactive agents registered and importable.

---

#### Component 3: Execution Flow Routing ✅

**File:** `src/orchestrators/{name}/{name}_orchestrator.py`

**Required Pattern in `execute()` method:**
```python
def execute(self, **kwargs) -> OrchestratorResult:
    # Phase 1: Analyze request
    request_analysis = self._analyze_request(kwargs)
    
    # Phase 2: Mode selection
    if self._should_use_interactive_mode(kwargs):
        return self._execute_interactive_mode(request_analysis, kwargs)
    else:
        return self._execute_autonomous_mode(request_analysis, kwargs)
```

**Validation Commands:**
```bash
# Check for mode routing
grep -A 10 "def execute" src/orchestrators/planning/planning_orchestrator.py | grep "interactive"

# Check for both execution paths
grep "_execute_interactive_mode" src/orchestrators/planning/planning_orchestrator.py
grep "_execute_autonomous_mode" src/orchestrators/planning/planning_orchestrator.py
```

**Expected:** Conditional routing to interactive OR autonomous mode.

---

#### Component 4: Interactive Execution Method ✅

**File:** `src/orchestrators/{name}/{name}_orchestrator.py`

**Required Method:**
```python
def _execute_interactive_mode(
    self, 
    analysis: RequestAnalysis, 
    kwargs: Dict
) -> OrchestratorResult:
    """Execute in interactive mode with user collaboration."""
    
    # 1. Create session
    session = self.interactive_creation(
        name=kwargs["name"],
        user_context=kwargs.get("user_context", {})
    )
    
    # 2. Get agent
    agent = InteractivePlanner(config=self.config)
    
    # 3. Collaborate
    result_data = await agent.collaborate(session)
    
    # 4. Return result
    return self._create_success_result(result_data)
```

**Validation Commands:**
```bash
# Check if method exists
grep -n "_execute_interactive_mode" src/orchestrators/planning/planning_orchestrator.py

# Check for agent instantiation
grep "InteractivePlanner" src/orchestrators/planning/planning_orchestrator.py

# Check for session creation
grep "interactive_creation\|interactive_plan_creation" src/orchestrators/planning/planning_orchestrator.py
```

**Expected:** Method exists, instantiates agent, creates session, returns result.

---

#### Component 5: User Interface Bridge ✅

**File:** `src/orchestrators/{name}/user_interface.py` (NEW)

**Required Classes:**
```python
class QuestionFormatter:
    """Format questions for user display."""
    
    def format_multiple_choice(self, question: Question) -> str:
        pass
    
    def format_yes_no(self, question: Question) -> str:
        pass
    
    def format_free_text(self, question: Question) -> str:
        pass

class ResponseParser:
    """Parse user responses."""
    
    def parse_answer(self, question: Question, user_input: str) -> Answer:
        pass

class ConversationManager:
    """Manage interactive conversation flow."""
    
    def ask_question(self, question: Question) -> Answer:
        pass
    
    def present_draft(self, draft_data: Dict) -> bool:
        pass
    
    def collect_feedback(self) -> List[str]:
        pass
```

**Validation Commands:**
```bash
# Check if UI bridge exists
test -f src/orchestrators/planning/user_interface.py || echo "MISSING: UI bridge"
test -f src/orchestrators/ado/user_interface.py || echo "MISSING: UI bridge"

# Check for required classes
grep "class QuestionFormatter" src/orchestrators/planning/user_interface.py
grep "class ResponseParser" src/orchestrators/planning/user_interface.py
grep "class ConversationManager" src/orchestrators/planning/user_interface.py
```

**Expected:** UI bridge file exists with all 3 classes.

---

#### Component 6: Integration Tests ✅

**File:** `tests/orchestrators/{name}/test_interactive_workflow.py`

**Required Tests:**
```python
def test_decision_logic_explicit_request():
    """Test interactive mode triggered by explicit request."""
    pass

def test_decision_logic_complexity_tier4():
    """Test interactive mode triggered by complexity."""
    pass

def test_decision_logic_low_confidence():
    """Test interactive mode triggered by ambiguity."""
    pass

def test_mode_routing_to_interactive():
    """Test execution routes to interactive mode."""
    pass

def test_mode_routing_to_autonomous():
    """Test execution routes to autonomous mode."""
    pass

def test_agent_instantiation():
    """Test interactive agent can be instantiated."""
    pass

def test_session_creation():
    """Test session creation succeeds."""
    pass

def test_end_to_end_interactive_workflow():
    """Test full interactive workflow from request to finalization."""
    pass
```

**Validation Commands:**
```bash
# Check if test file exists
test -f tests/orchestrators/planning/test_interactive_workflow.py || echo "MISSING: Integration tests"

# Run interactive tests
python3 -m pytest tests/orchestrators/planning/test_interactive_workflow.py -v

# Check test count
python3 -m pytest tests/orchestrators/planning/test_interactive_workflow.py --collect-only | grep "test session"
```

**Expected:** ≥8 tests, all passing.

---

### 1.5c. Wiring Status Report

Generate status report for all orchestrators:

```bash
# Create wiring report
cat > cortex-brain/health-reports/interactive-wiring-status.md << 'EOF'
# Interactive Workflow Wiring Status Report

**Date:** $(date +%Y-%m-%d)

## Planning Orchestrator

| Component | Status | Notes |
|-----------|--------|-------|
| Decision Logic | ❌ | Method exists but not called in execute() |
| Agent Registration | ❌ | InteractivePlanner not in registry |
| Execution Routing | ❌ | No conditional routing in execute() |
| Interactive Method | ⚠️ | interactive_plan_creation exists but not used |
| UI Bridge | ❌ | user_interface.py missing |
| Integration Tests | ⚠️ | 29 mock tests exist, no real integration |

**Overall:** 🔴 0/6 components fully wired

## ADO Orchestrator

| Component | Status | Notes |
|-----------|--------|-------|
| Decision Logic | ❌ | Not implemented |
| Agent Registration | ❌ | InteractiveADOPlanner doesn't exist |
| Execution Routing | ❌ | Direct generation only |
| Interactive Method | ❌ | Not implemented |
| UI Bridge | ❌ | Not implemented |
| Integration Tests | ❌ | Not implemented |

**Overall:** 🔴 0/6 components implemented

EOF

cat cortex-brain/health-reports/interactive-wiring-status.md
```

### 1.5d. Automated Wiring Validation Script

```bash
# Create validation script
cat > scripts/validate_interactive_wiring.sh << 'EOF'
#!/bin/bash
# Interactive Workflow Wiring Validation Script

echo "🔍 Validating Interactive Workflow Wiring..."
echo ""

ORCHESTRATORS=("planning" "ado")
PASS=0
FAIL=0

for orch in "${ORCHESTRATORS[@]}"; do
  echo "📋 Checking $orch orchestrator..."
  
  # Check 1: Decision logic
  if grep -q "_should_use_interactive_mode" "src/orchestrators/$orch/${orch}_orchestrator.py" 2>/dev/null; then
    echo "  ✅ Decision logic exists"
    ((PASS++))
  else
    echo "  ❌ Decision logic MISSING"
    ((FAIL++))
  fi
  
  # Check 2: Agent registration
  if grep -q "interactive_$orch" "src/cortex_agents/agent_registry.py" 2>/dev/null; then
    echo "  ✅ Agent registered"
    ((PASS++))
  else
    echo "  ❌ Agent NOT registered"
    ((FAIL++))
  fi
  
  # Check 3: Execution routing
  if grep -A 5 "def execute" "src/orchestrators/$orch/${orch}_orchestrator.py" 2>/dev/null | grep -q "interactive"; then
    echo "  ✅ Execution routing present"
    ((PASS++))
  else
    echo "  ❌ Execution routing MISSING"
    ((FAIL++))
  fi
  
  # Check 4: Interactive method
  if grep -q "_execute_interactive_mode" "src/orchestrators/$orch/${orch}_orchestrator.py" 2>/dev/null; then
    echo "  ✅ Interactive method exists"
    ((PASS++))
  else
    echo "  ❌ Interactive method MISSING"
    ((FAIL++))
  fi
  
  # Check 5: UI bridge
  if [ -f "src/orchestrators/$orch/user_interface.py" ]; then
    echo "  ✅ UI bridge exists"
    ((PASS++))
  else
    echo "  ❌ UI bridge MISSING"
    ((FAIL++))
  fi
  
  # Check 6: Integration tests
  if [ -f "tests/orchestrators/$orch/test_interactive_workflow.py" ]; then
    echo "  ✅ Integration tests exist"
    ((PASS++))
  else
    echo "  ❌ Integration tests MISSING"
    ((FAIL++))
  fi
  
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results: $PASS passed, $FAIL failed"
TOTAL=$((PASS + FAIL))
PERCENT=$((PASS * 100 / TOTAL))
echo "Wiring Coverage: $PERCENT%"

if [ $PERCENT -eq 100 ]; then
  echo "✅ All interactive workflows fully wired!"
  exit 0
else
  echo "❌ Wiring incomplete. See: cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md"
  exit 1
fi
EOF

chmod +x scripts/validate_interactive_wiring.sh
./scripts/validate_interactive_wiring.sh
```

### 1.5e. Enforcement Rules

**⚠️ MANDATORY:** Before releasing ANY orchestrator with interactive components:

1. **All 6 components must be wired** (100% wiring coverage)
2. **Integration tests must pass** (end-to-end workflow verified)
3. **Wiring validation script must pass** (automated check)
4. **Documentation must be complete** (README updated with interactive mode)

**Prevention:** Add pre-commit hook to prevent merging unwired interactive code:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for new interactive components without wiring
if git diff --cached --name-only | grep -q "interactive.*\.py"; then
  echo "⚠️  Interactive component detected in commit."
  echo "Running wiring validation..."
  ./scripts/validate_interactive_wiring.sh
  if [ $? -ne 0 ]; then
    echo "❌ Commit rejected: Interactive component not fully wired."
    echo "Complete wiring before committing. See:"
    echo "cortex-brain/documents/analysis/interactive-workflow-wiring-gap-analysis.md"
    exit 1
  fi
fi
```

---

## Phase 2-4: Health & Diagnosticsp CORTEX 4.0 at peak performance through health checks, intent router validation, and automated prompt regeneration.

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 10-Phase Maintenance Pipeline

**⚠️ EVERY PHASE = DIAGNOSE + AUTO-REPAIR + VERIFY**

| Phase | Diagnose | Auto-Repair | Verify |
|-------|----------|-------------|--------|
| **1** | Check scaffold generators exist | Create missing generators | Test generation works |
| **1.5** | Check interactive wiring gaps | Wire all 6 components | Run integration tests |
| **2** | Quick health scan | Fix critical issues | Health score ≥90 |
| **3** | Full component diagnostic | Patch unwired components | All components functional |
| **4** | Detect wiring gaps | Patch source code | 100% wiring coverage |
| **4a** | Parse wiring reports | Execute auto_wire_orchestrators.py | Commit fixes to git |
| **4.5** | Run test suite | Delete obsolete tests, fix bugs | 100% pass rate |
| **5** | Scan knowledge library | Fix broken refs, sync YAML↔MD | All guidelines accessible |
| **6** | Check report age/size | Archive old reports, cleanup | Reports organized |
| **7** | Validate manifest paths | Fix broken references | All manifests synced |
| **8** | Measure prompt bloat | Regenerate lean prompts | Each <200 lines |
| **9** | Find duplicate reports | Delete duplicates, consolidate | Clean report structure |

---

## Phase 1: Toolkit Automation Validation 🛠️

### 1a. Verify Scaffold Generators Exist

**Critical:** Ensure automation utilities are present and functional.

```bash
# Check plan scaffold generator
test -f cortex-toolkit/core/utilities/plan_scaffold_generator.py || echo "ERROR: Plan scaffold generator missing!"

# Check orchestrator scaffold generator
test -f cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py || echo "ERROR: Orchestrator scaffold generator missing!"

# Verify both are registered in toolkit manifest
grep -q "plan-scaffold" cortex-toolkit/toolkit-manifest.yaml || echo "ERROR: Plan scaffold not registered!"
grep -q "orchestrator-scaffold" cortex-toolkit/toolkit-manifest.yaml || echo "ERROR: Orchestrator scaffold not registered!"
```

### 1a-2. Verify Interactive Planning Session ✨ NEW

**Critical:** Ensure interactive planning workflow is properly wired.

```bash
# Check interactive session module exists
test -f src/orchestrators/planning/interactive_session.py || echo "ERROR: Interactive session module missing!"

# Verify session states are defined
grep -q "class SessionState" src/orchestrators/planning/interactive_session.py || echo "ERROR: SessionState enum missing!"

# Check for key workflow classes
grep -q "class PlanningSession" src/orchestrators/planning/interactive_session.py || echo "ERROR: PlanningSession class missing!"
grep -q "class DiscoveryEngine" src/orchestrators/planning/interactive_session.py || echo "ERROR: DiscoveryEngine class missing!"
grep -q "class ApprovalWorkflow" src/orchestrators/planning/interactive_session.py || echo "ERROR: ApprovalWorkflow class missing!"
grep -q "class CleanupPhase" src/orchestrators/planning/interactive_session.py || echo "ERROR: CleanupPhase class missing!"
```

**Expected Workflow States:**
- `INITIALIZING` → `DISCOVERY` → `CONTEXT_GATHERING` → `USER_REVIEW`
- `USER_REVIEW` → `APPROVED` or `REFINING`
- `APPROVED` → `DRAFTING` → `CLEANUP` → `FINALIZED`

**Test Interactive Planning:**
```bash
# Run interactive planning tests (29 tests expected)
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py -v

# Expected: 18 session tests + 11 workflow tests = 29 total
```

### 1a-3. Verify Vision API Auto-Engagement 👁️ NEW

**Critical:** Ensure Vision API automatically engages when images are attached.

```bash
# Check vision orchestrator exists
test -f src/tier1/vision_orchestrator.py || echo "ERROR: Vision orchestrator missing!"

# Check image detector exists
test -f src/tier1/image_detector.py || echo "ERROR: Image detector missing!"

# Check vision context middleware
test -f src/operations/utilities/vision_context_middleware.py || echo "ERROR: Vision context middleware missing!"

# Verify auto-detection is enabled in config
grep -q "auto_detect_images" cortex.config.json || echo "WARNING: Auto-detect not configured!"
grep -q "auto_analyze_on_detect" cortex.config.json || echo "WARNING: Auto-analyze not configured!"
```

**Expected Features:**
- ✅ Automatic image detection in chat attachments
- ✅ Auto-engage Vision API without user prompting
- ✅ Context injection into planning/debugging workflows
- ✅ Duplicate image caching (24hr TTL)
- ✅ Token budget enforcement (500 token limit)

**Test Vision Auto-Engagement:**
```python
# Smoke test: Verify vision orchestrator detects images
from src.tier1.vision_orchestrator import VisionOrchestrator
from src.tier1.image_detector import ImageDetector

# Load config
import json
with open('cortex.config.json') as f:
    config = json.load(f)

# Initialize orchestrator
orchestrator = VisionOrchestrator(config)

# Test image detection (dry run)
result = orchestrator.process_request(
    user_request="analyze this",
    attachments=[
        {'type': 'image', 'path': '/path/to/test.png', 'mime': 'image/png'}
    ]
)

print(f"✅ Images found: {result['images_found']}")
print(f"✅ Auto-analyze: {orchestrator.auto_analyze}")
print(f"✅ Auto-inject: {orchestrator.inject_context}")
```

### 1b. Test Scaffold Generators

```bash
# Test plan scaffold generator (dry run)
python cortex-toolkit/core/utilities/plan_scaffold_generator.py "test-plan" --dry-run

# Test orchestrator scaffold generator (dry run)
python cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py --type planning "test-plan" --dry-run

# List available templates
python cortex-toolkit/core/utilities/orchestrator_scaffold_generator.py --list-templates
```

**Expected Output:**
- ✅ Dry run shows 4 folders for planning (context, reports, artifacts, tracking)
- ✅ progress-tracker.json would be created
- ✅ All orchestrator templates listed (planning, sanitization, tdd, ado, maintenance)

### 1c. Verify Manifest Integration

Check that planning system manifest references automation:

```bash
# Verify automation section exists in planning manifest
grep -A 5 "automation:" cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml
```

**Expected Fields:**
- `tool:` points to `plan_scaffold_generator.py`
- `usage:` shows command syntax
- `benefits:` lists automation advantages
- `enforcement:` references maintenance requirement

### 1d. Enforcement Rule

**⚠️ MANDATORY:** All new plans MUST use scaffold generator.

**Manual folder creation is DEPRECATED** as of CORTEX 4.0.1.

**Validation:** During Phase 7 (Regenerate Prompts), verify CORTEX.prompt.md and planning-system-4.0-manifest.yaml both enforce scaffold usage.

---

## Phase 2-4: Health Diagnostics + Auto-Repair

### Phase 2: Quick Health Check (DIAGNOSE)

```bash
# Run quick health diagnostic
python3 scripts/cortex_system_doctor.py --quick
```

**Expected Output:** Health score with breakdown of issues.

### Phase 3: Full Diagnostic (DEEP SCAN)

```bash
# Run comprehensive system scan
python3 scripts/cortex_system_doctor.py --phase diagnose --phase scan
```

**Expected Output:** Detailed report of all unwired components, duplicates, unnecessary files.

### Phase 4: Wiring Integrity Check (DETECT GAPS)

```bash
# Detect wiring gaps (generates report for Phase 4a)
python3 scripts/check_wiring_integrity.py
```

**Expected Output:** JSON report showing which components are unwired.

**⚠️ CRITICAL:** Phases 2-4 are DIAGNOSTIC ONLY. They identify problems but **DO NOT FIX THEM**.

**Next:** Phase 4a AUTO-REPAIRS the issues identified above.

---

## Phase 4a: Auto-Wire Components 🔥 NEW - CRITICAL FOR PERSISTENCE

### ⚠️ WHY THIS PHASE IS MANDATORY

**Problem:** Running maintenance on Machine A and committing changes does NOT wire components on Machine B after `git pull`.

**Root Cause:** Phases 2-4 are **diagnostic only** - they generate reports but **don't modify source code**.

**Solution:** Phase 4a **patches source files** to fix wiring gaps, making changes **git-committable** and **persistent across machines**.

**Reference:** `cortex-brain/documents/analysis/maintenance-wiring-persistence-gap.md`

### 4a. Run Auto-Wiring Script

```bash
# Preview what will be fixed (dry-run, default)
python3 scripts/auto_wire_orchestrators.py

# Apply wiring fixes to source code
python3 scripts/auto_wire_orchestrators.py --execute

# Verify 100% wiring coverage
python3 scripts/check_wiring_integrity.py
```

**Expected Output:**
```
🔧 CORTEX Auto-Wiring Script v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Wiring Gaps Detected:
  ❌ Planning Orchestrator: Decision logic not called
  ❌ Agent Registry: InteractivePlanner missing

🔧 Applying Fixes...
  [1/4] Wiring decision logic... ✅ SUCCESS (18 lines modified)
  [2/4] Creating agent registry... ✅ SUCCESS (23 lines added)
  [3/4] Wiring execution method... ⏭️  SKIPPED (exists)
  [4/4] Updating operations config... ✅ SUCCESS (1 field modified)

✅ Wiring Coverage: 100% (was 50%)
```

### 4b. Commit Wiring Fixes

**⚠️ CRITICAL:** These changes MUST be committed to persist across machines.

```bash
# Review changes
git diff src/orchestrators/ src/cortex_agents/ cortex-operations.yaml

# Stage wiring fixes
git add src/orchestrators/planning/planning_orchestrator.py
git add src/cortex_agents/agent_registry.py
git add cortex-operations.yaml

# Commit with descriptive message
git commit -m "fix: auto-wire planning orchestrator interactive mode

- Added interactive mode check in execute() method
- Created agent_registry.py with InteractivePlanner registration
- Updated cortex-operations.yaml with interactive_mode flag

Wiring coverage: 50% → 100%
Generated by: scripts/auto_wire_orchestrators.py"

# Push to remote
git push origin CORTEX-4.0
```

### 4c. Verify Persistence on Another Machine

```bash
# On Machine B (fresh clone or pull)
git pull origin CORTEX-4.0

# Verify wiring WITHOUT running auto-wire script
python3 scripts/check_wiring_integrity.py

# Expected: 100% wiring coverage (no manual fixes needed)
```

**Success Criteria:**
- ✅ Auto-wire script runs without errors
- ✅ Source files modified (planning_orchestrator.py, agent_registry.py, cortex-operations.yaml)
- ✅ Wiring check shows 100% coverage
- ✅ Changes committed and pushed to remote
- ✅ `git pull` on Machine B shows 100% wiring (without re-running auto-wire)

### 4d. Troubleshooting

**Issue:** Auto-wire script fails with "No wiring report found"

**Solution:**
```bash
# Generate fresh wiring report first
python3 scripts/check_wiring_integrity.py
# Then run auto-wire
python3 scripts/auto_wire_orchestrators.py --execute
```

**Issue:** Wiring coverage still <100% after auto-wire

**Solution:**
```bash
# Check which components are still unwired
python3 scripts/check_wiring_integrity.py | grep "❌"
# Review auto-wire log for skipped patterns
cat cortex-brain/health-reports/auto-wire-log-*.txt
```

**Issue:** Need to undo auto-wiring changes

**Solution:**
```bash
# Restore from automatic backups
python3 scripts/auto_wire_orchestrators.py --undo
# Or manually restore from .bak files
ls -lah src/**/*.bak.*
```

---

## Phase 4.5: Test Suite Health 🧪 - ZERO TOLERANCE POLICY

### ⚠️ CRITICAL ENFORCEMENT RULE

**NO TEST FAILURES ALLOWED.** Period.

If tests fail during maintenance:
1. **Identify root cause** - Is functionality broken OR is test obsolete?
2. **Fix or DELETE** - Either fix the code OR delete the obsolete test
3. **Never settle** - "99% pass rate" = FAILURE. Target is 100%.

### When to Run Tests

Run the full test suite during maintenance when:
- ✅ **Interactive planning system** has been modified
- ✅ **Core orchestrators** have been updated
- ✅ **Brain protection rules** have changed
- ✅ **Fixture patterns** need validation
- ❌ **Minor documentation updates** (skip tests)
- ❌ **Knowledge library additions** (skip tests unless validation required)

### Test Suite Execution

**⚠️ CRITICAL: Always run tests SEQUENTIALLY (never in parallel) to avoid race conditions and flaky test results.**

```bash
# Run full planning orchestrator test suite SEQUENTIALLY (MUST be 100% passing)
python3 -m pytest tests/orchestrators/planning/ --tb=short -v -n0

# REQUIRED: 100% pass rate (no failures, no errors, no skips without justification)
# -n0 flag ensures sequential execution (no parallel workers)

# Run core functionality tests only (faster validation) - SEQUENTIAL
python3 -m pytest tests/orchestrators/planning/test_interactive_planning_session.py \
                 tests/orchestrators/planning/test_toolkit_integration.py \
                 tests/orchestrators/planning/test_interactive_workflow_integration.py -v -n0

# REQUIRED: 100% passing (currently 42/48 total core tests)

# Alternative: Use Python test runner script for sequential execution
python3 run_tests_sequential.py tests/orchestrators/planning/

# Use test runner script for specific categories (all run sequentially)
./test_planning.sh interactive   # Interactive session workflow
./test_planning.sh toolkit        # Toolkit integration
./test_planning.sh wiring         # Interactive wiring validation
./test_planning.sh quick          # Core functionality only
./test_planning.sh all            # Full suite
```

### Test Health Metrics - ZERO TOLERANCE

| Metric | REQUIRED | Action if NOT Met |
|--------|----------|-------------------|
| **Core Tests Pass Rate** | **100%** | **STOP MAINTENANCE - Fix immediately or delete obsolete tests** |
| **Full Suite Pass Rate** | **100%** | **DELETE obsolete tests or refactor to match current functionality** |
| **Error Count** | **0** | **CRITICAL - Fix all errors before continuing** |
| **Failure Count** | **0** | **CRITICAL - No failures allowed** |
| **Test Execution Time** | <30s | Acceptable, monitor for regression |

### Obsolete Test Detection & Deletion Protocol

**When functionality changes (e.g., Planning orchestrator refactored), tests MUST be updated or deleted.**

#### Step 1: Identify Obsolete Tests

```bash
# Run tests and capture failures
python3 -m pytest tests/orchestrators/planning/ -v --tb=line 2>&1 | tee test_results.txt

# Look for these patterns indicating obsolete tests:
grep -E "(AttributeError|ImportError|ModuleNotFoundError)" test_results.txt
grep -E "test.*old.*api" test_results.txt
grep -E "DEPRECATED|LEGACY|OLD" tests/orchestrators/planning/*.py
```

**Red Flags for Obsolete Tests:**
- ❌ Tests for methods/classes that no longer exist
- ❌ Tests importing deprecated modules
- ❌ Tests with `@pytest.mark.skip` without clear justification
- ❌ Tests passing but not exercising actual code paths (mocks everything)
- ❌ Tests for APIs that were refactored but tests weren't updated

#### Step 2: Classify Failures

For EACH failing test, determine:

**A. Obsolete Test (DELETE)**
- Tests code that was intentionally removed/refactored
- Tests deprecated APIs with no replacement
- Tests mock-heavy scenarios that don't validate real behavior
- Tests marked "TODO" or "WIP" for >30 days

**B. Misaligned Test (REFACTOR)**
- Tests valid functionality but uses old API
- Tests correct behavior but with wrong assertions
- Tests proper code path but with outdated fixtures

**C. Real Bug (FIX CODE)**
- Tests valid, current functionality that's actually broken
- Tests core behavior that should work but doesn't

#### Step 3: Execute Cleanup

```bash
# Create cleanup manifest
cat > /tmp/test_cleanup_plan.md << 'EOF'
# Test Cleanup Plan - $(date +%Y-%m-%d)

## Tests to DELETE (Obsolete)
- [ ] tests/orchestrators/planning/test_old_planning_api.py - Uses deprecated PlanningOrchestrator v3 API
- [ ] tests/orchestrators/planning/test_legacy_validation.py - Tests removed ValidationEngine

## Tests to REFACTOR (Misaligned)
- [ ] tests/orchestrators/planning/test_execute_workflow.py - Update to use new execute() signature
- [ ] tests/orchestrators/planning/test_plan_generation.py - Update fixtures for new folder structure

## Tests to FIX (Real Bugs)
- [ ] tests/orchestrators/planning/test_error_handling.py - Core error handling broken, fix orchestrator

## Justification
- Functionality changed: Planning orchestrator refactored in CORTEX 4.0.1 with interactive wiring
- Old tests validate APIs that no longer exist
- New tests created: test_interactive_workflow_integration.py (19 tests)
EOF

# Review and approve cleanup plan
cat /tmp/test_cleanup_plan.md

# DELETE obsolete tests (after approval)
git rm tests/orchestrators/planning/test_old_*.py
git rm tests/orchestrators/planning/test_legacy_*.py

# Commit cleanup
git add -A
git commit -m "test: delete obsolete planning tests after orchestrator refactor

- Removed tests for deprecated v3 API
- Removed tests for removed ValidationEngine
- Kept: 42 core tests (100% passing)
- Added: test_interactive_workflow_integration.py (19 tests)

Justification: Planning orchestrator refactored with interactive wiring.
Old tests validate non-existent APIs. New tests cover current functionality."
```

#### Step 4: Validate 100% Pass Rate

```bash
# Run tests again - MUST be 100% passing
python3 -m pytest tests/orchestrators/planning/ -v

# If ANY test fails:
# - Go back to Step 1
# - Do NOT proceed with maintenance until 100% passing

# Generate cleanup report
python3 scripts/generate_test_cleanup_report.py \
  --before test_results.txt \
  --after test_results_clean.txt \
  --output cortex-brain/documents/reports/test-suite-cleanup-$(date +%Y%m%d).md
```

### Common Test Failure Patterns & Solutions

| Failure Pattern | Root Cause | Solution |
|----------------|------------|----------|
| `AttributeError: 'Orchestrator' object has no attribute 'old_method'` | Method removed during refactor | **DELETE** test (obsolete) |
| `ModuleNotFoundError: No module named 'old_module'` | Module renamed/removed | **DELETE** test (obsolete) |
| `AssertionError: Expected 'old_value' but got 'new_value'` | Behavior changed intentionally | **REFACTOR** test assertions |
| `RuntimeError: Config missing required key` | New config requirements | **REFACTOR** fixtures |
| `TypeError: execute() missing 1 required positional argument` | Signature changed | **REFACTOR** test calls |
| Tests pass but coverage shows code not executed | Over-mocked, not testing real code | **REFACTOR** to use real implementations |

### Test Refactoring Guidelines

When refactoring tests to match new functionality:

**1. Update Fixtures**
```python
# OLD (obsolete)
@pytest.fixture
def orchestrator():
    return PlanningOrchestrator()  # Old API, no config

# NEW (current)
@pytest.fixture
def orchestrator():
    config = {
        "cortex_root": "/path/to/CORTEX",
        "brain_dir": "cortex-brain",
    }
    return PlanningOrchestrator(config=config)  # New API
```

**2. Update Method Calls**
```python
# OLD (obsolete)
result = orchestrator.generate_plan(name="test")

# NEW (current)
result = orchestrator.execute(feature_name="test", interactive=False)
```

**3. Update Assertions**
```python
# OLD (obsolete)
assert result.status == "success"

# NEW (current)
assert result.status == OrchestratorStatus.SUCCESS
assert result.data["mode"] == "autonomous"
```

**4. Reduce Mocking**
```python
# OLD (over-mocked, doesn't test real behavior)
@patch('orchestrator.generate')
@patch('orchestrator.validate')
@patch('orchestrator.render')
def test_execute(mock_render, mock_validate, mock_generate):
    # Test passes but doesn't validate actual orchestrator behavior
    pass

# NEW (tests real integration)
def test_execute_autonomous_mode(orchestrator, tmp_path):
    # Use real orchestrator with real filesystem
    result = orchestrator.execute(feature_name="test", output_dir=tmp_path)
    assert result.status == OrchestratorStatus.SUCCESS
    # Validates real file creation, not mocked behavior
```

### Maintenance Enforcement

**❌ BLOCKING CONDITION:** If test pass rate < 100%, maintenance CANNOT proceed.

**Required Actions:**
1. ✅ Identify ALL failing tests
2. ✅ Classify each as Obsolete / Misaligned / Real Bug
3. ✅ DELETE obsolete tests immediately
4. ✅ REFACTOR misaligned tests to match current API
5. ✅ FIX real bugs in code
6. ✅ Re-run tests - MUST achieve 100% pass rate
7. ✅ Commit cleanup with detailed justification
8. ✅ Generate test cleanup report

**Only then** can maintenance continue to next phase.

### Test Report Location

After running tests and cleanup, check:
- `cortex-brain/documents/reports/test-suite-cleanup-{DATE}.md` for cleanup report
- Report MUST show: Before → After with 100% pass rate achieved

---

## Phase 5: Knowledge Library Validation 📚 CRITICAL

### 5a. Knowledge Library Structure Check

**Source of Truth:** `cortex-brain/knowledge/`

Verify knowledge library structure and accessibility:

```bash
# Verify knowledge library structure
test -d cortex-brain/knowledge || echo "ERROR: Knowledge library missing!"

# Count knowledge files by category
for dir in cortex-brain/knowledge/*/; do
  echo "$(basename "$dir"): $(find "$dir" -name "*.yaml" | wc -l) files"
done

# Verify README exists and is current
test -f cortex-brain/knowledge/README.md || echo "ERROR: Knowledge README missing!"

# Check for orphaned YAML files (not in a category)
find cortex-brain/knowledge/ -maxdepth 1 -name "*.yaml" -type f
```

**Expected Categories:**
- `database/` - Database best practices (Oracle, SQL Server, etc.)
- `ddd/` - Domain-Driven Design patterns
- `devops/` - DevOps and infrastructure
- `domains/` - Domain-specific knowledge (RAG, embeddings)
- `engineering/` - Software engineering principles
- `performance/` - Performance optimization
- `security/` - Security best practices
- `testing/` - Testing strategies and patterns
- `ui-ux/` - UI/UX design guidelines

### 5b. Knowledge Library Reference Validation

**Critical:** Ensure orchestrators and modules can reference knowledge library.

Verify these systems wire to knowledge library:

| System | Knowledge Usage | Verification |
|--------|----------------|--------------|
| **Code Review Orchestrator** | Validates code against guidelines | Check manifest references `cortex-brain/knowledge/` |
| **Sanitization Orchestrator** | Applies best practices during cleanup | Check for knowledge library imports |
| **Refactoring Orchestrator** | Identifies anti-patterns | Check pattern detection references |
| **TDD Orchestrator** | Guides test design | Check test pattern references |
| **Documentation Generator** | Auto-generates docs from guidelines | Check template references |

### 5c. Knowledge Library Sync Validation (NEW)

**Critical:** Ensure markdown templates stay in sync with YAML knowledge library.

```bash
# Run knowledge library sync check
python3 scripts/sync_knowledge_library.py --check-status

# Generate sync report
python3 scripts/sync_knowledge_library.py --report > cortex-brain/health-reports/knowledge-sync-report.md
```

**Expected Output:**
```
📊 Knowledge Library Sync Status

✅ glassmorphism-design-standards: none (in sync)
⚠️  [other-file]: sync_md_to_yaml (markdown changed)
```

**If out of sync detected:**
```bash
# Dry run to preview changes
python3 scripts/sync_knowledge_library.py --sync-all --dry-run

# Perform sync (updates hashes, flags manual review)
python3 scripts/sync_knowledge_library.py --sync-all
```

**Sync Registry Files:**
- `glassmorphism-design-standards.yaml` ↔ `glassmorphism-design-standards-v2.md`
- Future template ↔ YAML pairs automatically detected via `metadata.sync` section

### 5d. Knowledge File Schema Validation

Each knowledge YAML must have:

```yaml
metadata:
  title: "Guideline Name"
  category: "Category"
  version: "X.Y"
  created: "YYYY-MM-DD"
  updated: "YYYY-MM-DD"
  tags: [tag1, tag2, ...]
  
  # Sync configuration (if synced with markdown template)
  sync:
    source_markdown: "cortex-brain/documents/templates/filename.md"
    sync_enabled: true
    sync_direction: "bidirectional"
    last_sync: "2025-12-29T00:00:00Z"
  
  generated_docs:
    - path: "docs/guidelines/{category}/{filename}.md"

{category}_section:
  principle: "Core principle statement"
  importance: "Why it matters"
  rules:
    - id: "unique_id_###"
      name: "Rule Name"
      severity: "CRITICAL|HIGH|MEDIUM|LOW"
      examples:
        good: [...]
        bad: [...]
```

### 5d. Validation Commands

```bash
# Check all YAML files for metadata section
for f in cortex-brain/knowledge/**/*.yaml; do
  grep -q "metadata:" "$f" || echo "MISSING metadata: $f"
done

# Verify severity levels are valid
for f in cortex-brain/knowledge/**/*.yaml; do
  grep -E "severity: \"(CRITICAL|HIGH|MEDIUM|LOW)\"" "$f" > /dev/null || \
    echo "Invalid severity in: $f"
done

# Check for duplicate rule IDs
grep -rh "id: \"" cortex-brain/knowledge/ | sort | uniq -d

# Verify README is up to date (check statistics)
grep "Total:" cortex-brain/knowledge/README.md
```

### 5e. Integration Verification

Verify orchestrators can load knowledge library:

```bash
# Check for knowledge library imports in orchestrators
grep -r "knowledge" src/orchestrators/*.py | grep -E "(import|load|read)"

# Check for knowledge references in manifests
grep -r "knowledge" cortex-brain/manifests/orchestrators/*.yaml

# Verify brain protection rules reference knowledge library
grep -A 5 "knowledge" cortex-brain/brain-protection-rules.yaml
```

### 5f. Knowledge Library Health Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Total Guidelines | 30 | 30+ | ✅ |
| Categories | 9 | 8+ | ✅ |
| Total Rules | 525+ | 500+ | ✅ |
| Critical Rules | 77+ | 75+ | ✅ |
| Files with Metadata | 30/30 | 100% | ✅ |
| Files with Examples | 30/30 | 100% | ✅ |

---

## Phase 6: Review Reports

```bash
# Phase 5: Reports in cortex-brain/health-reports/
ls -lah cortex-brain/health-reports/
```

---

## Phase 7: Intent Router Validation ⚠️ CRITICAL

### 7a. Manifest Path Verification

**Source of Truth:** `cortex-brain/manifests/orchestrators/`

Scan all orchestrator manifests and verify CORTEX.prompt.md references them correctly:

| Manifest File | Orchestrator | Must Have Triggers |
|---------------|--------------|-------------------|
| `planning-system-4.0-manifest.yaml` | Planning System | `plan [x]`, `create a plan`, `make a plan` |
| `tdd-orchestrator-v4-manifest.yaml` | TDD Mastery | `start tdd`, `run tests`, `tdd [x]` |
| `ado-planning-manifest.yaml` | ADO Operations | `plan ado`, `ado story`, `ado feature` |
| `code-sanitization-manifest.yaml` | Sanitization | `sanitize`, `make generic`, `anonymize` |
| `refinement-orchestrator-manifest.yaml` | Refinement | `refine`, `improve cortex` |

### 7b. Output Structure Validation

Planning System MUST specify folder structure from manifest:
```yaml
output_location: cortex-brain/documents/planning/active/{PLAN_NAME}/
required_subfolders: [context/, reports/, artifacts/, tracking/]
required_files: [00-master-plan.md]
```

### 6c. Validation Commands

```bash
# Check for broken/old paths
grep -r "orchestrator-manifests" .github/prompts/  # Should return NOTHING

# Verify all manifest references exist
for f in $(grep -oh "cortex-brain/manifests/orchestrators/[^\"']*" .github/prompts/*.md); do
  [ -f "$f" ] || echo "MISSING: $f"
done
```

---

## Phase 8: Regenerate Lean Prompts (WITH COMPLETE INTENT ROUTER WIRING)

**Goal:** Create minimal, clean prompt files with proper intent routing for ALL orchestrators.

**Reference:** `cortex-brain/documents/analysis/orchestrator-inventory-2025-12-29.md`

### 8a. Pre-Regeneration: Orchestrator Discovery

**BEFORE regenerating prompts, scan ALL orchestrator manifests:**

```bash
# List all orchestrator manifests
find cortex-brain/manifests/orchestrators/ -name "*-manifest.yaml" -o -name "*-orchestrator*.yaml"

# Extract orchestrator names and capabilities
grep -h "orchestrator_name:" cortex-brain/manifests/orchestrators/*.yaml
```

**Required Orchestrators for Intent Router (Minimum 8):**

1. **Planning System** - `planning-system-4.0-manifest.yaml`
2. **TDD Mastery** - `tdd-orchestrator-v4-manifest.yaml`
3. **Debug Orchestrator** - `debug-orchestrator-manifest.yaml`
4. **CORTEX Lens** - `cortex-lens-v3-manifest.yaml`
5. **ADO Planning** - `ado-planning-manifest.yaml`
6. **Code Sanitization** - `code-sanitization-manifest.yaml`
7. **Refinement** - `refinement-orchestrator-manifest.yaml`
8. **System Maintenance** - `cortex-maintenance.prompt.md`

**Optional but Recommended:**
- Onboarding (via `onboarding_interactive.py`)
- Technical Documentation (`technical-documentation-orchestrator-manifest.yaml`)

### 8b. CORTEX.prompt.md COMPLETE Structure (Target: <200 lines)

**Template with ALL orchestrators wired:**

```markdown
# 🎯 CORTEX Universal Entry Point

**Version:** 4.0.1 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Website:** https://asifhussain60.github.io/CORTEX/  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## ⚠️ Parse User Request FIRST

Remove meta-directives before intent classification:
- `Follow instructions in...` → REMOVE
- `Use *.prompt.md...` → REMOVE  
- `Reference file:///...` → REMOVE

---

## 🚨 PLANNING DETECTION (HIGHEST PRIORITY)

**⛔ STOP! Check this FIRST before ANY work:**

### Planning Command Patterns (MUST create plan, NOT implement):
- `/CORTEX Plan [feature]`
- `/CORTEX plan [feature]`
- `create a plan for [feature]`
- `make a plan for [feature]`
- `plan: [feature]`
- `planning [feature]`

### Implementation Patterns (Execute without planning):
- `implement [feature]`
- `build [feature]`
- `create [feature]` (without "plan")
- `add [feature]`
- `fix [issue]`

### ⛔ MANDATORY RULE:
**If ANY planning pattern detected → STOP → Create plan structure → DO NOT IMPLEMENT**

### Example Detection:
```
User: "/CORTEX Plan user authentication"
✅ CORRECT: Create planning/active/user-authentication/ + 4 subfolders → STOP
❌ WRONG: Start implementing auth code

User: "implement user authentication"  
✅ CORRECT: Begin implementation directly
❌ WRONG: Create a plan first
```

---

## 🔀 Intent Router

| Command | Orchestrator | Manifest | Output |
|---------|--------------|----------|--------|
| `/CORTEX Plan [x]`, `create a plan`, `make a plan`, `plan: [x]` | **Planning System** | `planning-system-4.0-manifest.yaml` | `planning/active/{NAME}/` + 4 subfolders **→ STOPS HERE** |
| `start tdd`, `run tests`, `tdd [x]` | TDD Mastery | `tdd-orchestrator-v4-manifest.yaml` | Tests in `tests/` |
| `debug [issue]`, `fix bug`, `troubleshoot` | Debug Orchestrator | `debug-orchestrator-manifest.yaml` | Bug report + fix |
| `open lens`, `show dashboard`, `analytics` | CORTEX Lens | `cortex-lens-v3-manifest.yaml` | Dashboard visualization |
| `onboard`, `getting started`, `learn cortex` | Onboarding | Via `onboarding_interactive.py` | Interactive 6-phase guide |
| `plan ado`, `ado story`, `ado feature` | ADO Operations | `ado-planning-manifest.yaml` | ADO work items |
| `sanitize`, `make generic`, `anonymize` | Sanitization | `code-sanitization-manifest.yaml` | Sanitized codebase |
| `refine`, `improve cortex`, `optimize code` | Refinement | `refinement-orchestrator-manifest.yaml` | 7-phase improvement |
| `system maintenance`, `health check` | Maintenance | Via `cortex-maintenance.prompt.md` | Health reports |
| `help`, `show commands` | Help | Template-based | Command list |

**Manifest Path:** `cortex-brain/manifests/orchestrators/{manifest-file}`

### ⚠️ Planning vs. Implementation

**Planning Commands = Create folder structure ONLY (NO CODE):**
- `/CORTEX Plan user-auth` → Creates `planning/active/user-auth/` + subfolders → **STOPS**
- `create a plan for API` → Creates `planning/active/api/` + subfolders → **STOPS**

**Implementation Commands = Execute code directly:**
- `implement user-auth` → Writes code immediately (no plan creation)
- `build API endpoint` → Creates files immediately (no plan creation)

### Planning System Output Structure

All plans MUST create:
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md    # Main plan
├── context/             # Context artifacts
├── reports/             # Progress reports
├── artifacts/           # Supporting files
└── tracking/            # progress-tracker.json
```

---

## 📋 Response Format (v4.0)

**Header (ALWAYS):**
```markdown
## 🧠 CORTEX {Title}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
```

**Body (Adaptive):**

| Tier | Tokens | Structure |
|------|--------|-----------|
| INSTANT | <50 | `{answer}` |
| FOCUSED | 50-200 | `{explanation}` + `**Next:**` |
| STRUCTURED | 200-600 | `**Context:**` + `**Changes:**` + `**Next:**` |
| COMPREHENSIVE | 600+ | Multiple `### {Sections}` |

**Next Steps:** EXACTLY ONE action OR `✅ All work complete!`

**Completion (when ALL work done):**
```markdown
# 🎉 CONGRATULATIONS
## 🧠 CORTEX {Operation}
...
✅ **All work complete!** No further action required.
```

---

## 🛡️ Brain Protection (SKULL)

| Rule | Enforcement |
|------|-------------|
| **TDD_ENFORCEMENT** | RED→GREEN→REFACTOR mandatory |
| **HOLISTIC_DISCOVERY** | Search before create (prevent duplication) |
| **REFACTOR_CLEANUP** | Remove orphaned/duplicate code |
| **GIT_ISOLATION** | CORTEX code never in user repos |
| **PLANNING_ISOLATION** | Planning commands create plans ONLY, never implement |

**Full rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs (`CORTEX/summary.md`)

**✅ REQUIRED:** `cortex-brain/documents/{category}/`

Categories: `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

```
cortex-brain/                    src/
├── tier0/ (Governance)          ├── tier0-3/ (Brain tiers)
├── tier1/ (Working memory)      ├── cortex_agents/ (2 agents)
├── tier2/ (Knowledge graph)     ├── orchestrators/ (8 workflows)
├── tier3/ (Dev context)         └── response_templates/
└── manifests/orchestrators/
```

---

## 📋 Quick Reference

| Command | Description |
|---------|-------------|
| `/CORTEX Plan [feature]` | Create planning folder (NO implementation) |
| `start tdd` | RED→GREEN→REFACTOR workflow |
| `debug [issue]` | Investigate and fix bug |
| `open lens` | Show analytics dashboard |
| `system maintenance` | 6-phase health pipeline |
| `sanitize [dir]` | Remove company data |
| `refine` | 7-phase system improvement |
| `help` | Show all commands |

---

## 📚 Resources

- **Learning:** `cortex-brain/documents/learning-paths/`
- **Templates:** `cortex-brain/response-templates-v4.yaml`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Maintenance:** `.github/prompts/cortex-maintenance.prompt.md`

---

**Quick Start:** Say `help` to see all operations.

**Anti-Bloat:** This file MUST stay under 200 lines.
```

### 8c. copilot-instructions.md COMPLETE Structure (Target: <150 lines)

**Template with ALL operations referenced:**

```markdown
# GitHub Copilot Instructions for CORTEX

**Purpose:** AI Assistant with long-term memory, context awareness, and strategic planning  
**Version:** 4.0.1 | **Author:** Asif Hussain

---

## 🎯 Entry Point

**Primary:** Load `.github/prompts/CORTEX.prompt.md` for all intent routing.

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled
- **User repos**: User operations only

---

## 🔀 Intent Routing

All command routing is defined in `CORTEX.prompt.md`. Key orchestrators:

| Intent Pattern | Route To |
|----------------|----------|
| `plan`, `create a plan`, `make a plan` | Planning System → folder with 4 subfolders **→ NO IMPLEMENTATION** |
| `tdd`, `start tdd`, `run tests` | TDD Orchestrator → RED→GREEN→REFACTOR |
| `debug`, `fix bug`, `troubleshoot` | Debug Orchestrator → investigation + fix |
| `lens`, `dashboard`, `analytics` | CORTEX Lens → visualization |
| `ado`, `ado story`, `ado feature` | ADO Operations → work items |
| `sanitize`, `make generic` | Sanitization → 5-phase cleanup |
| `maintenance`, `health check` | Maintenance → 6-phase pipeline |
| `refine`, `improve` | Refinement → 7-phase improvement |

**Manifest Location:** `cortex-brain/manifests/orchestrators/`

---

## 📋 Response Format

Defer to `CORTEX.prompt.md` for full spec. Summary:

- **Header:** Always include `## 🧠 CORTEX {Title}` + author line
- **Body:** Scales with complexity (INSTANT → COMPREHENSIVE)
- **Next Steps:** EXACTLY ONE action OR completion message
- **Completion:** Use `# 🎉 CONGRATULATIONS` when all work done

---

## 🛡️ Brain Protection (SKULL)

| Rule | Action |
|------|--------|
| TDD_ENFORCEMENT | Tests must fail before implementation |
| HOLISTIC_DISCOVERY | Search before create (prevent duplication) |
| GIT_ISOLATION | CORTEX code never commits to user repos |
| PLANNING_ISOLATION | Planning commands create plans ONLY, never implement |

**Full rules:** `cortex-brain/brain-protection-rules.yaml`

---

## 📁 Document Organization

**⛔ FORBIDDEN:** Root-level docs  
**✅ REQUIRED:** `cortex-brain/documents/{category}/`

Categories: `reports/`, `analysis/`, `summaries/`, `investigations/`, `planning/`, `implementation-guides/`

---

## 🏗️ Architecture

```
cortex-brain/           # Long-term memory (4-tier brain)
├── tier0/ (Governance) 
├── tier1/ (Working memory)
├── tier2/ (Knowledge graph)
├── tier3/ (Dev context)
└── manifests/orchestrators/

src/                    # Implementation
├── cortex_agents/      # 2 specialist agents
├── orchestrators/      # 8 workflow orchestrators
└── response_templates/ # Template rendering
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Intent router (source of truth) |
| `.github/prompts/cortex-maintenance.prompt.md` | 6-phase maintenance |
| `cortex-brain/brain-protection-rules.yaml` | SKULL rules |
| `cortex-brain/response-templates-v4.yaml` | Response templates |
| `cortex-brain/manifests/orchestrators/` | All orchestrator manifests |

---

## 🚀 Quick Start

Say `help` in Copilot Chat to see all operations.

**For maintenance:** Use `system maintenance` to run 6-phase health pipeline.

---

**Anti-Bloat:** This file MUST stay under 150 lines. All details defer to CORTEX.prompt.md.
```

### 8d. Wiring Rules

1. **Single Source of Truth:** `CORTEX.prompt.md` is the intent router
2. **copilot-instructions.md:** Points TO CORTEX.prompt.md, doesn't duplicate
3. **ALL Manifests:** Every orchestrator in `cortex-brain/manifests/orchestrators/` MUST be in Intent Router
4. **Minimum 3 Triggers:** Each orchestrator needs ≥3 command patterns
5. **Output Specs:** All operations include clear output specification
6. **Planning Isolation:** Planning commands include "→ STOPS HERE" or "→ NO IMPLEMENTATION"
7. **SKULL Integration:** PLANNING_ISOLATION rule referenced in both files
8. **Knowledge Library:** All orchestrators reference `cortex-brain/knowledge/` for guidelines

### 8e. Auto-Repair Actions

When regenerating prompts, AUTOMATICALLY:

1. **Scan** `cortex-brain/manifests/orchestrators/` for all `.yaml` files
2. **Extract** orchestrator names and capabilities
3. **Populate** Intent Router table with ALL orchestrators (minimum 8)
4. **Add** 3+ trigger patterns per orchestrator
5. **Specify** output location/format for each orchestrator
6. **Verify** all manifest paths resolve to existing files
7. **Enforce** line limits: CORTEX.prompt.md <200, copilot-instructions.md <150
8. **Validate** no duplicate entries between files
9. **Ensure** PLANNING_ISOLATION rule in SKULL section
10. **Backup** existing files before overwriting

### 8f. Validation Commands

```bash
# Check all orchestrators are wired
for manifest in cortex-brain/manifests/orchestrators/*-manifest.yaml; do
  orchestrator=$(basename "$manifest" | sed 's/-manifest.yaml//')
  grep -q "$orchestrator" .github/prompts/CORTEX.prompt.md || echo "MISSING: $orchestrator"
done

# Verify no broken paths
grep -r "orchestrator-manifests" .github/prompts/  # Should return NOTHING

# Verify all manifest references exist
for f in $(grep -oh "cortex-brain/manifests/orchestrators/[^\"']*" .github/prompts/*.md); do
  [ -f "$f" ] || echo "MISSING: $f"
done

# Check line counts
wc -l .github/prompts/CORTEX.prompt.md  # Should be <200
wc -l .github/copilot-instructions.md   # Should be <150
```

---

## ✅ Success Criteria

| Check | Pass Condition |
|-------|----------------|
| Health Score | ≥ 90/100 |
| Wiring Coverage | 100% |
| **Intent Router Completeness** 🆕 | **Minimum 8 orchestrators with 3+ triggers each** |
| **Interactive Wiring** 🆕 | All 6 components for Planning & ADO orchestrators |
| Knowledge Library | All 9 categories present, README current |
| Knowledge Guidelines | 30+ files with valid metadata |
| Knowledge Integration | Orchestrators reference knowledge library |
| Manifest Paths | All resolve to existing files |
| Intent Triggers | Each orchestrator has ≥3 triggers |
| CORTEX.prompt.md | <200 lines, **ALL orchestrators wired** |
| copilot-instructions.md | <150 lines, defers to CORTEX.prompt.md |
| Output Structures | Planning System has folder spec |
| **PLANNING_ISOLATION** 🆕 | **Rule enforced in both prompt files** |
| **Interactive Planning** 🆕 | Session workflow tests 100% passing |
| **Vision Auto-Engagement** 🆕 | Image detection and analysis wired |
| **Test Suite Health** 🆕 | **100% pass rate (ZERO failures, ZERO errors, ZERO obsolete tests)** |

---

## 📋 Validation Checklist

Run during every maintenance cycle:

### Core System
- [ ] Health score ≥90
- [ ] All manifest paths resolve to existing files
- [ ] No references to deprecated `orchestrator-manifests/` path
- [ ] Each orchestrator has ≥3 trigger phrases
- [ ] Planning System has output folder structure specified
- [ ] CORTEX.prompt.md is <200 lines
- [ ] copilot-instructions.md is <150 lines
- [ ] copilot-instructions.md defers to CORTEX.prompt.md (no duplication)
- [ ] Reports folder cleaned (see Phase 9)

### Intent Router Completeness 🆕
- [ ] Planning System orchestrator in Intent Router
- [ ] TDD Mastery orchestrator in Intent Router
- [ ] Debug Orchestrator in Intent Router
- [ ] CORTEX Lens orchestrator in Intent Router
- [ ] ADO Planning orchestrator in Intent Router
- [ ] Code Sanitization orchestrator in Intent Router
- [ ] Refinement orchestrator in Intent Router
- [ ] System Maintenance orchestrator in Intent Router
- [ ] Onboarding/Help orchestrator in Intent Router
- [ ] Minimum 8 orchestrators total in Intent Router
- [ ] All orchestrators have 3+ trigger patterns
- [ ] All orchestrators have output specifications
- [ ] Planning commands include "→ STOPS HERE" or "→ NO IMPLEMENTATION" indicator
- [ ] PLANNING_ISOLATION rule in SKULL section of CORTEX.prompt.md
- [ ] PLANNING_ISOLATION rule in SKULL section of copilot-instructions.md
- [ ] copilot-instructions.md mirrors ALL primary operations from CORTEX.prompt.md
- [ ] No orchestrator manifests exist without Intent Router entry

### Interactive Wiring 🆕
- [ ] Decision logic exists in Planning & ADO orchestrators
- [ ] Decision logic is CALLED in execute() method
- [ ] Interactive agents registered in agent_registry.py
- [ ] Execution flow has conditional routing (interactive vs autonomous)
- [ ] Interactive execution method implemented and functional
- [ ] UI bridge exists (user_interface.py) for question/answer handling
- [ ] Integration tests cover end-to-end interactive workflow
- [ ] Wiring validation script passes: `./scripts/validate_interactive_wiring.sh`
- [ ] Interactive wiring coverage: 100% for active orchestrators
- [ ] Pre-commit hook prevents unwired interactive code

### Knowledge Library
- [ ] Knowledge library has all 9 categories present
- [ ] Knowledge library README.md is current (stats match actual files)
- [ ] All knowledge YAML files have valid metadata section
- [ ] All knowledge rules have valid severity levels (CRITICAL/HIGH/MEDIUM/LOW)
- [ ] No duplicate rule IDs across knowledge library
- [ ] Orchestrators reference knowledge library in code/manifests
- [ ] Brain protection rules reference knowledge library

### Interactive Planning 🆕
- [ ] Interactive session module exists (`src/orchestrators/planning/interactive_session.py`)
- [ ] SessionState enum with 8 states (INITIALIZING → FINALIZED)
- [ ] PlanningSession, DiscoveryEngine, ApprovalWorkflow, CleanupPhase classes exist
- [ ] Session state transitions validated (DISCOVERY → CONTEXT_GATHERING → USER_REVIEW → APPROVED → DRAFTING → CLEANUP → FINALIZED)
- [ ] Interactive planning tests: 29/29 passing (100%)
- [ ] End-to-end workflow test passing (full lifecycle validation)
- [ ] Conversation history tracking operational
- [ ] Iterative refinement loop functional

### Vision API Auto-Engagement 🆕
- [ ] Vision orchestrator exists (`src/tier1/vision_orchestrator.py`)
- [ ] Image detector exists (`src/tier1/image_detector.py`)
- [ ] Vision context middleware exists (`src/operations/utilities/vision_context_middleware.py`)
- [ ] Config has `auto_detect_images: true`
- [ ] Config has `auto_analyze_on_detect: true`
- [ ] Config has `auto_inject_context: true`
- [ ] Image detection works for PNG, JPG, JPEG formats
- [ ] Vision API auto-engages without user prompting
- [ ] Duplicate image caching operational (24hr TTL)
- [ ] Token budget enforcement active (500 token limit)
- [ ] Context injection into planning/debugging workflows verified

### Test Suite Health 🆕
- [ ] Core tests (interactive + toolkit + wiring): **100% passing (ZERO failures)**
- [ ] Full planning test suite: **100% passing (ZERO failures)**
- [ ] Error count: **0 (MANDATORY)**
- [ ] Failure count: **0 (MANDATORY)**
- [ ] Test execution time: <30 seconds
- [ ] Obsolete tests **DELETED** (tests for removed/refactored APIs)
- [ ] Misaligned tests **REFACTORED** (tests updated to match current functionality)
- [ ] Test cleanup report generated in `cortex-brain/documents/reports/`
- [ ] Cleanup report shows Before → After with 100% achievement
- [ ] Git commit includes detailed justification for deleted tests

---

## Phase 9: Report Management 🗑️

**Goal:** Prevent report bloat - user won't read them, CORTEX doesn't need most of them.

### 9a. Report Policy

| Report Type | Policy | Reason |
|-------------|--------|--------|
| **Timestamped operational logs** (cleanup-*, brain-tuning-*, architectural-review-*) | DELETE | Ephemeral, no reference value |
| **Benchmark/test results** (benchmark_*, DOC_QUALITY_REPORT_*) | DELETE | Temporary test data |
| **Task completion summaries** (story-*, planning-*, feature-*) | DELETE | User won't read, redundant |
| **Duplicate analyses** (unwired-components-TIMESTAMP-*) | DELETE | Keep only latest if needed |
| **Major architecture decisions** (SYSTEM-INTEGRITY-*, MOCK-STUB-AUDIT) | KEEP | Reference for future decisions |
| **Migration/refactor summaries** (ORCHESTRATOR-*, CORTEX-CLEANUP-*) | KEEP | Historical context |

### 8b. Cleanup Commands

```bash
cd cortex-brain/documents/reports/

# Delete timestamped operational JSONs
rm -f cleanup-*.json architectural-review-*.json brain-tuning-*.json

# Delete benchmark/test JSONs
rm -f benchmark_*.json DOC_QUALITY_REPORT_*.json summary_*.json

# Delete task completion summaries
rm -f story-*.md planning-*.md feature-*.md *-complete.md

# Delete duplicate analyses (keep only one if needed)
rm -f unwired-components-2025*.json unwired-components-2025*.md

# Delete operational JSONs
rm -f git-sync-*.json validation_report.json system-alignment-report-*.json

# Verify cleanup
echo "Remaining reports: $(ls -1 | wc -l)"
du -sh .
```

### 8c. Prevention Rules

**STOP creating reports for:**
- ❌ Task completion summaries
- ❌ Incremental progress updates  
- ❌ Operational logs with timestamps
- ❌ Benchmark results (use metrics database instead)

**ONLY create reports for:**
- ✅ Major architectural decisions
- ✅ System-wide migrations/refactors
- ✅ Compliance audits (when required)
- ✅ Reference documentation (non-temporal)

### 8d. Alternative: Use Metrics Database

For tracking operational data, use `cortex-brain/analytics/metrics.db` instead of JSON reports.

---