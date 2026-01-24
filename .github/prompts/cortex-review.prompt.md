# CORTEX Review System - 8-Agent Comprehensive Analysis
**Version:** 5.0 | **Updated:** 2026-01-24 | **Authority:** cortex-impl-map.yaml v3.0 | **Status:** ✅ PRODUCTION READY

---

## ⚠️ CRITICAL: Response Header Enforcement (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Review
**Author:** Asif Hussain | **Phase:** Analysis | **Orchestrator:** ReviewOrchestrator ✅

---
```

---

## 🎯 What This Does

CORTEX Review is your **code quality watchdog**. It performs comprehensive analysis using 8 specialized agents that scan your codebase for problems you might miss:

- **Brittleness** → Finds fragile code that could break under stress
- **Hallucination** → Catches AI safety & output validation issues
- **Governance** → Ensures compliance with CORTEX rules (CORE-001 through CORE-029)
- **Assumptions** → Uncovers hidden dependencies & platform assumptions
- **Debt** → Identifies duplicated code, TODOs, and technical shortcuts
- **State/Concurrency** → Detects race conditions, deadlocks, thread safety issues
- **Architecture** → Spots SOLID violations, tight coupling, design problems
- **Integration/Observability** → Finds monitoring gaps and missing observability

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
Scans everything. Takes ~60 minutes. Best for periodic audits.

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
| `/review` | All 8 | 60 min | Full audit, production readiness |
| `/review {file}` | All 8 | 20 min | Specific file deep dive |
| `/review-quick` | BRIT, GOV, DEBT | 15 min | Fast health check |
| `/review-safety` | HALL, ASM, STATE | 20 min | Security & safety focus |
| `/review-quality` | DEBT, ARCH, INTEG | 25 min | Code quality & design |
| `/review-brittleness` | BRIT only | 10 min | Fault tolerance check |
| `/review-hallucination` | HALL only | 10 min | AI safety check |
| `/review-governance` | GOV only | 10 min | Rule compliance |
| `/review-assumptions` | ASM only | 8 min | Dependency check |
| `/review-debt` | DEBT only | 12 min | Code duplication |
| `/review-state` | STATE only | 10 min | Thread safety |
| `/review-arch` | ARCH only | 12 min | Design patterns |
| `/review-integration` | INTEG only | 10 min | Observability |

---

## 🤖 What Each Agent Looks For

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

### 🟡 Agent 3: Governance (GOV)
**Question:** Does this follow CORTEX rules?

**Checks for:**
- Missing type hints (CORE-011)
- Missing docstrings (CORE-012)
- Bare `except:` clauses (CORE-013)
- No audit logging (CORE-027)
- Tests written after code (CORE-008)

**Example Finding:** "Function `process_data()` missing type hints and docstring"

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

### 🖤 Agent 8: Integration/Observability (INTEG)
**Question:** Can we see what's happening in production?

**Checks for:**
- Missing health check endpoints
- Untraced operations (hard to debug)
- Insufficient logging (can't diagnose issues)
- Missing metrics (can't see performance)
- Undocumented APIs
- Missing error reporting

**Example Finding:** "Database queries don't appear in logs or metrics—no visibility"

---

## 📊 How Reviews Work (4 Phases)

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

### Phase 3: 8-Agent Deep Dive (30 min)
All 8 agents run in parallel, each scanning for their specialty:
- **Batch 1:** Brittleness, Hallucination, Governance (10 min each)
- **Batch 2:** Assumptions, Debt, State, Architecture, Integration (8-12 min each)

Outputs: `Findings-BRIT.yaml`, `Findings-HALL.yaml`, etc.

### Phase 4: Consolidation & Reporting (10 min)
I merge all findings and create:
- Priority-ordered issue list
- Remediation plan
- Executive summary
- Detailed recommendations

Output: `remediation-plan.yaml`, `review-consolidated.yaml`

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
- ✅ You have ~60 minutes free (or less for targeted reviews)
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

### Step 3: Analysis Runs (4 Phases, ~60 min)
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
