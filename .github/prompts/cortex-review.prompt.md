# CORTEX Review System - 10-Agent Comprehensive Analysis (ENHANCED)
**Version:** 5.2 | **Updated:** 2026-01-25 | **Authority:** cortex-impl-map.yaml v3.0 | **Status:** ✅ PRODUCTION READY + IMPLEMENTATION TRUTH

---

## ⚠️ CRITICAL: Response Header Enforcement (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Review
**Author:** Asif Hussain | **Phase:** Analysis | **Orchestrator:** ReviewOrchestrator ✅

---
```

---

## 🎯 What This Does (ENHANCED v5.1)

CORTEX Review is your **code quality AND implementation truth watchdog**. It performs comprehensive analysis using **10 specialized agents** that scan your codebase and specifications for problems you might miss:

**NEW (v5.2):** Agent 0 verifies implementation truth (CORE-030) and detects duplicate implementations (CORE-035) BEFORE code quality analysis.

- **Implementation Truth** → Verifies claims match actual code (Phase 0, runs FIRST)
- **Brittleness** → Finds fragile code that could break under stress
- **Hallucination** → Catches AI safety & output validation issues
- **Governance** → Ensures compliance with CORTEX rules (CORE-001 through CORE-035)
- **Assumptions** → Uncovers hidden dependencies & platform assumptions
- **Debt** → Identifies duplicated code, TODOs, and technical shortcuts
- **State/Concurrency** → Detects race conditions, deadlocks, thread safety issues
- **Architecture** → Spots SOLID violations, tight coupling, design problems
- **Integration/Observability** → Finds monitoring gaps, MCP exposure, wiring completeness

---

## 🔄 CORTEX LENS → DoR → Approval Protocol

### Before EVERY Review:

**Step 1: Review Plan (Conversational)**
```markdown
## Review Plan

Here's what I'm about to do:

**The Analysis:**
I'll scan the entire CORTEX codebase using 8 specialized review agents that check for:
- Code brittleness & fault tolerance
- AI safety & hallucination risks
- Governance rule compliance
- Hidden assumptions & dependencies
- Technical debt & code quality
- Thread safety & concurrency issues
- Architecture & design patterns
- Integration & monitoring gaps

**Where:** {SCOPE} (e.g., cortex/ and cortex_brain/)  
**Output:** A detailed findings report with recommendations  
**Time:** About an hour

**Everything looks good to go.** Say **yes** to start, or tell me if you'd like to change anything.
```

**Step 2: Wait for User Approval**
- ✅ Accept: "yes", "proceed", "go ahead", "approve"
- ❌ Decline: "no", "cancel", "stop"
- 🔧 Modify: "modify: {request}" or "change scope to..."

**Step 3: Execute Review**

---

## 🚀 How to Use

### Full System Review
```
"Run a full review"
```
Scans everything. Takes ~95 minutes. Best for periodic audits.

### Targeted Reviews
```
"Review just brittleness"    → Find fragile code
"Review governance"          → Check CORE rule compliance  
"Check for technical debt"   → Find TODOs & duplication
"Review {filename}"          → Analyze one specific file
```

### What You'll Get
- 📊 Summary table showing findings by agent
- 🔴 Critical issues that need immediate attention
- 🟠 High-priority fixes before next phase
- 🟡 Medium-priority improvements
- 📋 Remediation plan with specific actions

---

## 🚀 Quick Commands (Advanced)

| Command | Agents | Time | Best For |
|---------|--------|------|----------|
| `/review` | All 10 (0-9) | 105 min | Full audit, production readiness |
| `/review {file}` | All 9 (1-9) | 20 min | Specific file deep dive |
| `/review-quick` | BRIT, GOV, DEBT | 15 min | Fast health check |
| `/review-safety` | HALL, ASM, STATE | 20 min | Security & safety focus |
| `/review-quality` | DEBT, ARCH, INTEG | 25 min | Code quality & design |
| `/review-truth` | TRUTH only | 12 min | Implementation verification |
| `/review-brittleness` | BRIT only | 10 min | Fault tolerance check |
| `/review-hallucination` | HALL only | 10 min | AI safety check |
| `/review-governance` | GOV only | 10 min | Rule compliance |
| `/review-assumptions` | ASM only | 8 min | Dependency check |
| `/review-debt` | DEBT only | 12 min | Code duplication |
| `/review-state` | STATE only | 10 min | Thread safety |
| `/review-arch` | ARCH only | 12 min | Design patterns |
| `/review-integration` | INTEG only | 10 min | Observability |

---

## 🤖 What Each Agent Looks For (ENHANCED v5.2)

### 🔍 Agent 0: Implementation Truth Verification (TRUTH) — NEW v5.2
**Question:** Do documentation claims match actual implementation?

**Critical Checks (CORE-030 Enforcement):**
- **Governance Claims vs Reality:** Verify CORE-035 "Single canonical" against duplicate files
- **AC-PERMANENT-FIX Verification:** Check git commits for claimed permanent fixes
- **Configuration Claims:** Verify .vscode/mcp.json, auto_wire_production defaults, etc.
- **Orchestrator Wiring Claims:** Check actual registry vs claimed percentages
- **Implementation Status Claims:** Verify "COMPLETE" status against code stubs

**Duplicate Implementation Detection (CORE-035):**
- ConversationProtocol: Search for multiple implementations in different paths
- Orchestrator classes: Detect conflicting class definitions
- Interface implementations: Find multiple versions of same interface
- MCP tool definitions: Check for duplicate tool names or conflicting schemas

**Evidence Sources:**
- Git log for AC-PERMANENT-FIX commits
- File system scans for duplicate class names
- Import analysis for conflicting paths
- Governance rule files vs actual compliance

**Finding Categories:**
- **TRUTH-001:** Documentation-implementation mismatch (e.g., "Claims auto_wire_production=True default but code shows False")
- **TRUTH-002:** Duplicate implementation violation (e.g., "ConversationProtocol exists in 2 paths")
- **TRUTH-003:** Missing implementation for claimed feature (e.g., "Claims .vscode/mcp.json exists but file missing")
- **TRUTH-004:** False AC-PERMANENT-FIX claim (e.g., "AC-PERMANENT-FIX-005 claimed but no git commit found")
- **TRUTH-005:** Governance rule violation (e.g., "CORE-035 marked COMPLETE but duplicates exist")

**Example Finding:** "TRUTH-002: ConversationProtocol duplicate violation - found in cortex/core/orchestrator/ AND cortex/brain/core/orchestrator/ with different implementations. Tests import from both paths causing conflicts."

---

### 🔴 Agent 1: Brittleness (BRIT)
**Question:** Will this code survive real-world stress?

**Checks for:**
- Single points of failure that could bring down the system
- Error handling that might silently fail
- Resource exhaustion (unbounded loops, uncapped collections)
- Missing timeouts on external calls
- Bottlenecks that could cause slowdowns under load

**Example Finding:** "External API call at line 45 has no timeout—could hang forever"

---

### 🟠 Agent 2: Hallucination (HALL)
**Question:** Is AI output safely validated before use?

**Checks for:**
- LLM output used directly without validation
- Prompt injection vulnerabilities
- Missing confidence thresholds
- Unvalidated trust boundaries
- AI safety guardrails

**Example Finding:** "LLM response at line 89 isn't validated before executing—injection risk"

---

### 🟡 Agent 3: Governance (GOV) — ENHANCED v5.2
**Question:** Does this follow CORTEX rules?

**Checks for:**
- Missing type hints (CORE-011)
- Missing docstrings (CORE-012)
- Bare `except:` clauses (CORE-013)
- No audit logging (CORE-027)
- Tests written after code (CORE-008)
- **NEW:** Implementation truth violations (CORE-030)
- **NEW:** Duplicate implementations (CORE-035)
- **NEW:** AC-PERMANENT-FIX regression checks

**CORE-030 Implementation Truth Checks:**
- Functions answering questions without checking actual code first
- Documentation claims not backed by grep_search or read_file evidence
- Default parameter assumptions without verification

**CORE-035 Single Canonical Checks:**
- Multiple class definitions with same name in different modules
- Conflicting interface implementations
- Import path ambiguity causing module confusion

**CORE-035 Deduplication Algorithm (NEW - Comprehensive):**

**Step 1: Identify Potential Duplicates**
```bash
# Search for duplicate class/function names
find cortex/ -name "*.py" -exec grep -l "^class \|^def " {} \; | sort | uniq -d

# Example output indicates potential duplicates to investigate
for file in cortex/orchestrators/core/*.py cortex_brain/core/orchestrator/*.py; do
  grep "^class ConversationProtocol\|^def execute_operation" "$file"
done
```

**Step 2: Determine Canonical Version**
For each duplicate found:
- Check `git log --follow` to see which was created first (original is canonical)
- Count usage: Which version is imported in tests/main? (used = canonical)
- Check recent commits: Which has newer fixes? (maintained = canonical)
- Verify governance: Does it have CORE-011/012/013 compliance? (compliant = canonical)

**Step 3: Create Consolidation Plan**
For each duplicate:
1. Delete non-canonical versions
2. Update ALL imports to use canonical location
3. Update test fixtures to import canonical only
4. Run full test suite to verify no breakage
5. Create commit: `feat(CORE-035): Consolidate {name} to canonical location`

**Step 4: Verify No Import Conflicts**
```python
# After consolidation, verify:
import sys
duplicates = {}
for name, mod in sys.modules.items():
    if mod and hasattr(mod, '__file__') and mod.__file__:
        key = mod.__file__.split('/')[-1]
        if key not in duplicates:
            duplicates[key] = []
        duplicates[key].append(name)

for key, mods in duplicates.items():
    if len(mods) > 1:
        print(f"CONFLICT: {key} imported as {mods}")  # Should be empty
```

**Example Finding:** "CORE-035 violation: ConversationProtocol implemented in 2 locations with conflicting behavior. Canonical: cortex/brain/core/orchestrator/conversation_protocol.py (maintained, CORE-011 compliant). Duplicate: cortex_brain/legacy/conversation_protocol.py (outdated, 2 CORE violations). Action: Delete duplicate, update 12 imports to canonical."

---

### 🟢 Agent 4: Assumptions (ASM)
**Question:** What could go wrong if the environment changes?

**Checks for:**
- Hardcoded paths that won't work on other systems
- Platform-specific code without fallbacks
- Undeclared version dependencies
- Implicit ordering assumptions
- Missing configuration flexibility

**Example Finding:** "Hardcoded `/usr/local/bin` path won't work on Windows"

---

### 🔵 Agent 5: Debt (DEBT)
**Question:** Where's the code smell and shortcut debt?

**Checks for:**
- Copy-paste duplication
- Long functions (>50 lines) that do too much
- Deprecated API usage
- TODO/FIXME comments that pile up
- Untested code paths
- Missing abstractions

**Example Finding:** "Lines 120-145 duplicated from lines 200-225—extract to method"

---

### 💜 Agent 6: State/Concurrency (STATE)
**Question:** Could threads step on each other?

**Checks for:**
- Race conditions on shared state
- Deadlock patterns (lock ordering issues)
- Non-atomic operations
- Global mutable state without protection
- Missing synchronization

**Example Finding:** "Shared list `cache` at line 50 accessed without lock—race condition"

---

### 🟤 Agent 7: Architecture (ARCH)
**Question:** Does this follow good design principles?

**Checks for:**
- Single Responsibility violations (classes doing too much)
- God classes (oversized, everything depends on it)
- Circular dependencies between modules
- Tight coupling (hard to test, modify, or replace)
- Feature envy (methods that know too much about other objects)

**Example Finding:** "Controller imports 12 different services—violates Single Responsibility"

---

### 🖤 Agent 8: Integration/Observability (INTEG) — ENHANCED v5.1
**Question:** Can we see what's happening in production? Are MCP tools exposed? Is wiring complete?

**Core Observability Checks:**
- Missing health check endpoints
- Untraced operations (hard to debug)
- Insufficient logging (can't diagnose issues)
- Missing metrics (can't see performance)
- Undocumented APIs
- Missing error reporting

**ENHANCED (v5.1): MCP Tool Exposure Checks:**
- Are orchestrators exposing `get_mcp_tools()` method? (18/23 missing)
- Do MCP tools have proper schemas and descriptions?
- Are tool implementations wired into MCPServer integration?

**ENHANCED (v5.1): Wiring Integration Checks:**
- Orchestrator auto-wiring: Do all 23 orchestrators appear in registry?
- Import statements: Are orchestrators imported in `__init__.py`?
- Dependency injection: Are dependencies properly resolved?

**ENHANCED (v5.1): CLI Entry Point Checks:**
- Are orchestrators accessible via CLI commands?
- Do `/review-*` commands resolve to correct agents?
- Is help text complete and accurate?

**Finding Categories (ENHANCED):**
- **MCP-INTEG-001:** Tool exposure incomplete (e.g., "Orchestrator X missing get_mcp_tools()")
- **MCP-INTEG-002:** MCPServer integration gap (e.g., "Tools defined but not exposed to server")
- **MCP-INTEG-003:** MCP toolkit violation (e.g., "Tool schema invalid or missing description")
- **WIRING-INTEG-001:** Orchestrator wiring gap (e.g., "Orchestrator not in registry")
- **WIRING-INTEG-002:** Import/dependency resolution issue (e.g., "Circular import detected")
- **CLI-INTEG-001:** CLI command incomplete (e.g., "`/review-agent` not wired to orchestrator")
- **CLI-INTEG-002:** Help/documentation missing (e.g., "No help text for command")
- **SPEC-INTEG-001:** Specification/implementation alignment (e.g., "Prompt says wired, code has NotImplementedError")

**NEW (v5.2): Deduplication & Consolidation Checks:**
- **DEDUP-001:** Duplicate class definitions (e.g., "ConversationProtocol in 2 modules")
- **DEDUP-002:** Conflicting implementations (e.g., "IntentRouter with different behavior")
- **DEDUP-003:** Import path ambiguity (e.g., "Tests import from 2 different locations")
- **CONSOLIDATION-001:** Missing consolidation (e.g., "Duplicate exists but not consolidated per CORE-035")
- **CONSOLIDATION-002:** Incomplete consolidation (e.g., "Duplicate deleted but imports not updated")

**Example Findings:** 
- "Tool exposure: 5/23 orchestrators expose MCP tools (CRITICAL gap)"
- "Database queries don't appear in logs or metrics—no visibility"
- "CLI command `/review-ssot` not wired to Agent 0"
- "DEDUP-001: ConversationProtocol duplicated in cortex/core AND cortex_brain/core with 14 imports split between them"
- "CONSOLIDATION-001: MasterOrchestrator appears in 3 locations - no single canonical version"

---

## 🔍 NEW: CORE-035 Deduplication Review Checklist

**MANDATORY FOR EVERY CODE REVIEW** - Run before approving merge:

### Pre-Review: Scan for Duplicates
```bash
# Find potential duplicates (same name, different files)
echo "🔍 Scanning for duplicate class/function definitions..."

for pattern in "ConversationProtocol" "MasterOrchestrator" "IntentRouter" "orchestrator_registry"; do
  echo ""
  echo "Pattern: $pattern"
  find cortex/ -name "*.py" -exec grep -l "^class $pattern\|^def $pattern" {} \;
done

# Find imports from multiple locations
echo ""
echo "🔍 Checking for split imports..."
grep -r "from cortex\|from cortex_brain" cortex/ tests/ | awk -F: '{print $NF}' | sort | uniq -d
```

### During Review: Deduplication Checklist

**For EVERY pull request, verify:**

- [ ] **No new duplicate classes** 
  - Grep for class name across entire cortex/ folder
  - If found elsewhere, is it truly different or a duplicate?
  
- [ ] **No new duplicate functions**
  - Check for function name duplicates
  - If found elsewhere, should they be one shared function?

- [ ] **Imports use CANONICAL location only**
  - All tests import from canonical path
  - Main code imports from canonical path
  - No imports from 2 different locations for same class

- [ ] **No competing implementations**
  - Example: ConversationProtocol should exist in ONE place only
  - All usages point to same location
  - No conflicting behavior between versions

- [ ] **Master orchestrator wiring complete**
  - All 23 orchestrators imported in `__init__.py`
  - All orchestrators registered with @orchestrator decorator
  - All orchestrators appear in orchestrator_registry.yaml
  - No import errors or circular dependencies

- [ ] **CORE-035 compliance verified**
  - Zero duplicate implementations of core classes
  - Single canonical version of each component
  - All imports use canonical location
  - Tests confirm no import conflicts

### Post-Merge: Verify Consolidation

If deduplication was performed:

- [ ] **Verify deleted files**
  - Non-canonical version deleted
  - No orphaned references to deleted file

- [ ] **Verify all imports updated**
  - Search for old import paths
  - Update ALL usages to canonical location
  - Verify test suite runs without import errors

- [ ] **Run full test suite**
  - All tests pass with canonical imports only
  - No import-related failures
  - Verify no circular dependency issues

- [ ] **Create consolidation commit**
  - Commit message: `feat(CORE-035): Consolidate {ComponentName} to canonical location`
  - Include details of what was consolidated
  - Link to old duplicate location if deleted

- [ ] **Update roadmap**
  - Add `AC-CONSOLIDATION-##` entry if consolidation is significant
  - Document which duplicates were consolidated
  - Note any issues encountered

---

## 📋 Master Orchestrator Wiring Verification

**NEW (v5.2): Mandatory Verification for Production Readiness**

On EVERY code review, verify:

```markdown
## ✅ Master Orchestrator Wiring Checklist

| Item | Status | Evidence |
|------|--------|----------|
| All 23 orchestrators registered | ✅ | DatabaseBackedRegistry (23/23 wired) |
| DatabaseBackedRegistry SSOT | ✅ | `cortex/orchestrators/core/database_registry.py` |
| Health checker active | ✅ | `cortex/orchestrators/core/health_checker.py` |
| 4-stage pipeline intact | ⏳ | Check `MasterOrchestrator.execute_operation()` |
| No import errors | ⏳ | `python -c "from cortex.orchestrators import *"` |
| No circular imports | ⏳ | Run pytest with import validation |
| Test coverage adequate | ⏳ | Check test_master_orchestrator.py coverage |

**Target Status:** All ✅ (23/23 orchestrators wired, 0 errors)

**Current Status (AC-PERMANENT-FIX-009):** 23/23 wired (100%) via DatabaseBackedRegistry

**Verification Command:**
```python
from cortex.orchestrators.core.database_registry import get_database_registry, initialize_registry
initialize_registry()
stats = get_database_registry().get_wiring_statistics()
print(f"Wired: {stats['total_wired']}/{stats['total_registered']}")
# Output: Wired: 23/23
```
```

**Example Finding (if wiring incomplete):**
```markdown
### WIRING-INTEG-003: Incomplete Master Orchestrator Wiring

- **Current:** 18/23 orchestrators wired (78%)
- **Missing:** PlanningOrchestrator, RefactoringOrchestrator, 3 others
- **Impact:** Those orchestrators not available via MasterOrchestrator.execute()
- **Evidence:** 
  - Missing from cortex/orchestrators/core/__init__.py imports
  - Not in orchestrator_registry.yaml
  - Tests show NotImplementedError when routed

**Fix:** Wire missing 5 orchestrators:
1. Import orchestrators in __init__.py
2. Add @orchestrator decorator if missing
3. Register in orchestrator_registry.yaml
4. Add routing logic in MasterOrchestrator.execute_operation()
5. Test each orchestrator's routing path
6. Update AC-PERMANENT-FIX-001 status if this completes wiring

**Commit:** `feat(CORE-035): Complete master orchestrator wiring (18→23 orchestrators)`
```

---

## 📊 How Reviews Work (5 Phases: -1 through 3)

### Phase -1: SSOT Verification (10 min) 🆕 CORTEX v5.1
**NEW in v5.1:** This phase MUST run FIRST before all other analysis.

**Purpose:** Verify that specifications match implementation. Prevents circular issue patterns.

**Agent 0: SSOT-Compliance (S)**
- Loads source of truth: `cortex-impl-map.yaml` v3.0
- Compares against: Prompt files, agent specifications, phase definitions
- Calculates metric divergence: Claimed orchestrator completion % vs actual code
- Identifies blocking issues: Prerequisites incomplete, phases out of order, dependencies unmet
- Decision logic:
  - **Divergence > 10%:** 🔴 **CRITICAL** - BLOCK all other agents, flag as blocking work
  - **Divergence 5-10%:** 🟠 **HIGH** - Flag but continue with all agents (investigate in Phase 4)
  - **Divergence < 5%:** ✅ **PASS** - Proceed to Phase 0 with confidence
- Expected findings categories:
  - **SSOT-001:** Metric divergence (e.g., "Claims X/23 orchestrators, DatabaseBackedRegistry shows Y/23")
  - **SSOT-002:** Blocking phase (e.g., "Phase 5 marked complete but Phase 2 incomplete")
  - **SSOT-003:** Specification mismatch (e.g., "Prompt says agent X wired, DatabaseBackedRegistry disagrees")
  - **SSOT-004:** Implementation gap (e.g., "MCP tools defined but orchestrators missing exposure")

Output: `review-ssot-verification.yaml` with divergence report and blocking assessment.

---

### Phase 0: Pre-Flight Check (5 min)
Before we start, I verify everything is ready:
- ✅ Test suite healthy (6,847+ tests)
- ✅ Audit trail complete
- ✅ Code is current
- ✅ No blockers

If anything fails, we investigate first.

### Phase 1: Gap Inventory (10 min)
I check the master plan (`cortex-impl-map.yaml`) and verify:
- Are COMPLETED features actually implemented?
- Any FALSE_COMPLETED phases that need attention?
- Missing critical code?

Output: `review-gap-inventory.yaml`

### Phase 2: Stub Detection (10 min)
I hunt for incomplete code:
- `NotImplementedError` placeholders
- Empty `pass` statements
- Blocking TODOs
- Mock/hardcoded returns

Output: `review-stubs.yaml`

### Phase 3: 9-Agent Deep Dive (35 min) 🆕 ENHANCED in v5.1
After SSOT verification, all 9 agents run in parallel (Agent 0 + original 8):
- **Phase -1 complete:** Confidence that spec matches implementation
- **Agent 0:** SSOT-Compliance issues (if any divergence found)
- **Agent 1-8:** Traditional code quality analysis
  - **Batch 1:** Brittleness, Hallucination, Governance (10 min each)
  - **Batch 2:** Assumptions, Debt, State, Architecture, Integration (8-12 min each)

Outputs: `review-ssot-verification.yaml`, `Findings-BRIT.yaml`, `Findings-HALL.yaml`, etc.

### Phase 4: Consolidation & Reporting (10 min)
I merge all findings from Phase -1 (SSOT) and Phases 1-3 (Code Quality):
- **Phase -1 SSOT findings first:** Specification divergence (if blocking)
- **Phase 1-3 findings:** Consolidated by priority
- Create:
  - Priority-ordered issue list (critical/high/medium/low)
  - Remediation roadmap
  - Executive summary
  - Detailed recommendations by agent

Output: `remediation-plan.yaml`, `review-consolidated.yaml` (includes SSOT + code quality findings)

---

## 📁 What You Get

---

## 📁 Where Results Go

**For Full Reviews:**
```
_workspaces/roadmap/reports/
└── review-consolidated-2026-01-24-143000.yaml
    ├── Gap inventory (what's incomplete)
    ├── Stubs found (placeholder code)
    ├── All 8 agent findings (prioritized)
    └── Remediation roadmap
```

**For Targeted Reviews:**
```
_workspaces/roadmap/issues/{DATE}/
├── review-gap-inventory.yaml          (Phase 1)
├── review-stubs.yaml                  (Phase 2)
├── Findings-BRIT.yaml                 (Agent 1)
├── Findings-HALL.yaml                 (Agent 2)
├── Findings-GOV.yaml                  (Agent 3)
├── Findings-ASM.yaml                  (Agent 4)
├── Findings-DEBT.yaml                 (Agent 5)
├── Findings-STATE.yaml                (Agent 6)
├── Findings-ARCH.yaml                 (Agent 7)
├── Findings-INTEG.yaml                (Agent 8)
└── remediation-plan.yaml              (Phase 4)
```

---

## 🎯 Issue Severity: What It Means

| Level | Badge | When to Fix | Examples |
|-------|-------|------------|----------|
| **CRITICAL** 🔴 | Stop the line | Right now | Security breach, data loss risk, unhandled crash paths |
| **HIGH** 🟠 | Before next release | This sprint | Missing validation, race condition, CORE violation |
| **MEDIUM** 🟡 | This quarter | Next few weeks | Code duplication, missing docstring, design issue |
| **LOW** 🔵 | When you can | Next month | Style issue, minor refactoring, edge case handling |
| **INFO** ⚪ | FYI only | No deadline | Observation, pattern note, future consideration |

---

## 📋 Example: What You'll See

```markdown
## 🧠 CORTEX Review Results
**Date:** 2026-01-24 | **Scope:** cortex/ + cortex_brain/ | **Time:** 65 minutes

---

### Executive Summary
- **Total Issues:** 28 findings
- **Critical:** 1 (fix today)
- **High:** 10 (fix this sprint)
- **Medium:** 14 (fix soon)
- **Low:** 3 (backlog)

---

### By Agent

| Agent | Issues | Critical | High | Medium | Low |
|-------|--------|----------|------|--------|-----|
| Brittleness | 3 | 0 | 1 | 2 | 0 |
| Hallucination | 2 | 1 | 1 | 0 | 0 |
| Governance | 5 | 0 | 2 | 3 | 0 |
| Assumptions | 4 | 0 | 0 | 3 | 1 |
| Debt | 8 | 0 | 3 | 5 | 0 |
| State | 1 | 0 | 1 | 0 | 0 |
| Architecture | 2 | 0 | 1 | 1 | 0 |
| Integration | 3 | 0 | 1 | 1 | 1 |

---

### 🔴 Critical Issues (Fix Today)

**HALL-001:** Unvalidated LLM Output
- **File:** `cortex/ai/responder.py:45`
- **Problem:** LLM response used directly without validation—injection risk
- **Fix:** Add output schema validation before using response

---

### 🟠 High Priority (This Sprint)

**BRIT-003:** Missing Timeout on External API
- **File:** `cortex/api/client.py:123`
- **Problem:** API call could hang indefinitely
- **Fix:** Add 30-second timeout

**GOV-002:** Type Hints Missing
- **Files:** 5 functions across orchestrators
- **Problem:** CORE-011 violation
- **Fix:** Add type hints to all function signatures

---

### 🟡 Medium Priority (This Quarter)

**DEBT-005:** Code Duplication
- **Files:** `cortex/orchestrators/` (lines 120-145 duplicate lines 200-225)
- **Problem:** Same logic in two places—maintenance risk
- **Fix:** Extract shared method

---

### 🟢 Recommended Actions

1. **Today:** Fix HALL-001 (validation)
2. **This Sprint:** Add timeout, fix type hints, fix race condition
3. **This Quarter:** Address debt items, improve architecture
4. **Ongoing:** Address low-priority items as you work nearby
```

---

## 🔌 For Developers (How to Use Review Results)

### After a Review, You'll Have:
1. **A prioritized list** of issues (critical → low)
2. **Specific file:line locations** for each issue
3. **Clear explanations** of why it matters
4. **Concrete fix suggestions** for each problem
5. **An estimated timeline** (today, this sprint, quarterly, etc.)

### Next Steps:
- Fix CRITICAL issues immediately (security/safety)
- Schedule HIGH issues in your next sprint
- Consider MEDIUM/LOW for future work
- Use the provided file paths to navigate directly to problems
- Check the remediation plan for dependencies (some fixes unlock others)

---

## 🔗 Advanced: How Reviews Work Under the Hood

### Review Orchestrator
```python
from cortex.orchestrators.review.review_orchestrator import ReviewOrchestrator

reviewer = ReviewOrchestrator()
results = reviewer.full_review(scope="cortex/")
```

### Governance Registry
```python
from cortex.brain.core.governance_registry import GovernanceRegistry

registry = GovernanceRegistry()
compliance = registry.check_compliance(path="cortex/")
```

### Audit Logger
```python
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = EnhancedAuditLogger.instance()
logger.log_operation_start(operation="REVIEW", scope="cortex/")
```

---

## ✅ Before You Ask for a Review

**Pre-Review Checklist:**
- ✅ You know what you want to check (full system? specific file? one agent?)
- ✅ You have ~95 minutes free (or less for targeted reviews)
- ✅ You're ready to act on findings (create issues, plan fixes)
- ✅ The system is in a good state (tests passing, no emergency)

**Quick Launch Requests:**
```
"Run a full code review"
"Review brittleness in cortex/orchestrators/"
"Check governance compliance"
"Quick health check (15 minutes)"
```

---

## 🎯 What to Do With Results

### Immediately After Review:
1. Skim the executive summary
2. Note any CRITICAL issues
3. Look at HIGH issues for your team
4. Check the remediation timeline

### In Your Sprint Planning:
1. Pick up the HIGH priority items
2. Estimate the effort
3. Add to sprint if bandwidth exists
4. Create follow-up tickets for MEDIUM items

### Over Time:
1. Tackle CRITICAL/HIGH as found
2. Fit MEDIUM into regular work
3. Use LOW items as "good to fix nearby" opportunities
4. Track remediation progress in git commits

---

## 🔌 Advanced: How Reviews Work Under the Hood

### Review Orchestrator
```python
from cortex.orchestrators.review.review_orchestrator import ReviewOrchestrator

reviewer = ReviewOrchestrator()
results = reviewer.full_review(scope="cortex/")
```

### Governance Registry
```python
from cortex.brain.core.governance_registry import GovernanceRegistry

registry = GovernanceRegistry()
compliance = registry.check_compliance(path="cortex/")
```

### Audit Logger
```python
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = EnhancedAuditLogger.instance()
logger.log_operation_start(operation="REVIEW", scope="cortex/")
```

---

## ✅ Your Review Workflow

### Step 1: Request Review
```
"Run a full review"
or
"Quick brittleness check on cortex/orchestrators/"
```

### Step 2: Pre-Flight Checks
I verify everything is ready:
- ✅ System healthy
- ✅ Tests passing
- ✅ No blockers

### Step 3: Analysis Runs (5 Phases, ~95 min)
- Phase 0: Pre-flight validation
- Phase 1: Gap inventory
- Phase 2: Stub detection
- Phase 3: 8-agent deep dive
- Phase 4: Consolidation & recommendations

### Step 4: You Get Results
- Prioritized issue list
- File:line locations
- Clear explanations
- Suggested fixes
- Timeline for action

### Step 5: Take Action
- Fix CRITICALs immediately
- Schedule HIGH issues
- Plan MEDIUM/LOW work
- Track progress
