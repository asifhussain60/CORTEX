# CORTEX Review System - 9-Agent Comprehensive Analysis (ENHANCED)
**Version:** 5.1 | **Updated:** 2026-01-24 | **Authority:** cortex-impl-map.yaml v3.0 | **Status:** ✅ PRODUCTION READY + SSOT VERIFICATION

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

CORTEX Review is your **code quality AND specification integrity watchdog**. It performs comprehensive analysis using **9 specialized agents** (was 8, now includes SSOT-Compliance) that scan your codebase and specifications for problems you might miss:

### **NEW: SSOT-Compliance (Agent 0)** 🔑
**→ Verifies specification matches implementation BEFORE other checks**

### **Existing Agents (1-8):**
- **Brittleness** → Finds fragile code that could break under stress
- **Hallucination** → Catches AI safety & output validation issues
- **Governance** → Ensures compliance with CORTEX rules (CORE-001 through CORE-029)
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

**The Analysis (ENHANCED):**
I'll scan the entire CORTEX codebase using 9 specialized review agents:

**Phase -1 (NEW): SSOT Verification**
- Verify CORTEX.prompt.md matches cortex-impl-map.yaml
- Detect specification divergence (alert if >5% gap)
- Identify blocking work before proceeding
- Ensure all metrics are truthful

**Phase 0-4: Existing review stages**
- Code brittleness & fault tolerance
- AI safety & hallucination risks
- Governance rule compliance (29 CORE rules)
- Hidden assumptions & dependencies
- Technical debt & code quality
- Thread safety & concurrency issues
- Architecture & design patterns
- Integration & monitoring gaps
- **NEW: MCP tool exposure & wiring completeness**

**Where:** {SCOPE} (e.g., cortex/ and cortex_brain/)  
**Output:** Detailed findings report with recommendations  
**Time:** About 90 minutes (added 30 min for SSOT verification + expanded INTEG checks)

**Everything looks good to go.** Say **yes** to start, or tell me if you'd like to change anything.
```

**Step 2: Wait for User Approval**
- ✅ Accept: "yes", "proceed", "go ahead", "approve"
- ❌ Decline: "no", "cancel", "stop"
- 🔧 Modify: "modify: {request}" or "change scope to..."

**Step 3: Execute Review**

---

## 🚀 How to Use

### Full System Review (RECOMMENDED)
```
"Run a full review"
```
Scans everything including SSOT verification. Takes ~90 minutes. Best for production readiness verification.

### Targeted Reviews
```
"Review just brittleness"    → Find fragile code
"Review governance"          → Check CORE rule compliance  
"Check for technical debt"   → Find TODOs & duplication
"Review MCP integration"     → NEW: Check tool exposure + wiring
"Review SSOT"                → NEW: Verify spec vs impl alignment
"Review {filename}"          → Analyze one specific file
```

### What You'll Get
- 📊 Summary table showing findings by agent
- 🔴 Critical issues that need immediate attention
- 🟠 High-priority fixes before next phase
- 🟡 Medium-priority improvements
- 📋 Remediation plan with specific actions
- 🔑 **NEW: SSOT verification report (specification alignment)**

---

## 🚀 Quick Commands (Advanced)

| Command | Agents | Time | Best For |
|---------|--------|------|----------|
| `/review` | SSOT, All 8 | 90 min | Full audit, production readiness |
| `/review-quick` | SSOT, BRIT, GOV, DEBT | 25 min | Fast health check with SSOT |
| `/review-ssot` | SSOT only | 10 min | Specification verification |
| `/review-mcp` | INTEG (expanded) | 15 min | MCP tool & wiring completeness |
| `/review-integration` | INTEG (expanded) | 20 min | Observability + MCP + CLI |
| `/review {file}` | All 9 | 25 min | Specific file deep dive |

---

## 🤖 What Each Agent Looks For (ENHANCED)

### 🔑 Agent 0: SSOT-Compliance (NEW - RUNS FIRST)
**Question:** Does specification match implementation?

**Checks for (PHASE -1):**
- **Metric Divergence:** Compare cortex-impl-map.yaml vs prompt files
  - Orchestrators wired: claimed vs actual
  - MCP tools: claimed vs actual
  - Test pass rate: claimed vs actual
  - Phase completion: promised vs verified
  
- **Specification Truthfulness:** CORE-001 enforcement
  - Any claims > 10% divergence from actual?
  - Are COMPLETE phases actually complete?
  - Any FALSE_COMPLETED statuses?
  
- **Blocking Work Identification:**
  - Integration gaps (WIRE modules written but not integrated?)
  - Missing wiring (orchestrators defined but not discoverable?)
  - Unimplemented features (CLI shortcuts, auto-wiring)?
  
- **Trust Boundary Violations:**
  - Specification says X, but code shows Y?
  - Where's the gap? Why?

**Example Finding:** 
```
🔴 CRITICAL: Specification Divergence Detected

Component: Orchestrator Wiring
Claimed: 20/23 (87%) [from CORTEX.prompt.md]
Actual: 3/23 (13%) [from code verification]
Divergence: 74 percentage points

Root Cause: WIRE-001/002/003 modules written but 
NOT integrated into MasterOrchestrator.initialize()

Blocking: YES - Phase 1 orchestrator wiring incomplete

Recommendation: Update specifications to match
reality, identify root cause, complete integration.
```

**Severity:** 🔴 CRITICAL if divergence > 10%  
**Action:** BLOCK other reviews, surface immediately

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

### 🟡 Agent 3: Governance (GOV)
**Question:** Does this follow CORTEX rules?

**Checks for:**
- Missing type hints (CORE-011)
- Missing docstrings (CORE-012)
- Bare `except:` clauses (CORE-013)
- No audit logging (CORE-027)
- Tests written after code (CORE-008)
- Specification authority violations (CORE-001)

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

### 🖤 Agent 8: Integration/Observability (INTEG - ENHANCED v5.1)
**Question:** Can we see what's happening in production? Are all components wired?

**Checks for (EXPANDED):**
- Missing health check endpoints
- Untraced operations (hard to debug)
- Insufficient logging (can't diagnose issues)
- Missing metrics (can't see performance)
- Undocumented APIs
- Missing error reporting

**NEW CHECKS (v5.1):**
- **MCP Tool Exposure (MCP-INTEG-001 through MCP-INTEG-003)**
  * Are all 15 tools exposed via get_mcp_tools()?
  * Do all 23 orchestrators have tool discovery?
  * Is MCPServer.list_tools() fully integrated?
  
- **Orchestrator Wiring Completeness (WIRING-INTEG-001 through WIRING-INTEG-002)**
  * Are WIRE-001/002/003 modules integrated?
  * Are all promised orchestrators discoverable?
  * Is auto-wiring infrastructure (CORE-031) implemented?
  
- **CLI Entry Point Verification (CLI-INTEG-001 through CLI-INTEG-002)**
  * Are all 5 promised CLI shortcuts implemented?
  * Are CLI shortcuts wired to orchestrator execution?
  
- **Specification Alignment (SPEC-INTEG-001)**
  * Does cortex-impl-map.yaml match actual code?
  * Are all COMPLETE phases actually complete?

**Example Finding (NEW):** 
```
🟠 HIGH: MCP Tool Exposure Incomplete
   15 tools defined, but only 5/23 orchestrators 
   expose get_mcp_tools(). 18 orchestrators missing.
   MCPServer integration incomplete.
   
   Fix: Add get_mcp_tools() to all 18 orchestrators
```

---

## 📊 How Reviews Work (5 Phases - ENHANCED)

### Phase -1: SSOT Verification (NEW - 10 min)
**RUNS FIRST - BEFORE ALL OTHER AGENTS**

Verify specification matches implementation:
- Compare cortex-impl-map.yaml vs prompt files
- Check all claimed metrics against code
- Identify divergence (flag if > 5%)
- Surface blocking work

Output: `review-ssot-verification.yaml`

**If 🔴 CRITICAL divergence found:**
- STOP other reviews
- Report divergence immediately
- Recommend specification update FIRST

**If ✅ Specification verified:**
- Proceed to Phase 0 (Pre-Flight)

---

### Phase 0: Pre-Flight Check (5 min)
Before we start, I verify everything is ready:
- ✅ Test suite healthy
- ✅ Audit trail complete
- ✅ Code is current
- ✅ No specification divergence (from Phase -1)

If anything fails, we investigate first.

---

### Phase 1: Gap Inventory (10 min - ENHANCED)
I check the master plan (`cortex-impl-map.yaml`) and verify:
- Are COMPLETED features actually implemented?
- Any FALSE_COMPLETED phases that need attention?
- Missing critical code?
- **NEW (v5.1): Integration gaps (wiring not integrated)?**
- **NEW (v5.1): WIRE modules written but not called?**
- **NEW (v5.1): MCP tools defined but not exposed?**

Output: `review-gap-inventory.yaml`

---

### Phase 2: Stub Detection (10 min)
I hunt for incomplete code:
- `NotImplementedError` placeholders
- Empty `pass` statements
- Blocking TODOs
- Mock/hardcoded returns

Output: `review-stubs.yaml`

---

### Phase 3: 9-Agent Deep Dive (40 min - ENHANCED)
All 9 agents run in sequence:
- **Agent 0 (SSOT):** 10 min - Specification verification (already done in Phase -1)
- **Batch 1:** Brittleness, Hallucination, Governance (8 min each)
- **Batch 2:** Assumptions, Debt, State, Architecture (6 min each)
- **Batch 3:** Integration/Observability ENHANCED (10 min - MCP + wiring + CLI)

Outputs: `Findings-SSOT.yaml`, `Findings-BRIT.yaml`, `Findings-HALL.yaml`, ... `Findings-INTEG.yaml`

---

### Phase 4: Consolidation & Reporting (10 min)
I merge all findings and create:
- Priority-ordered issue list
- Remediation plan
- Executive summary
- Detailed recommendations
- **NEW (v5.1): Specification alignment report**

Output: `remediation-plan.yaml`, `review-consolidated.yaml`

---

## 📁 Where Results Go

**For Full Reviews:**
```
_workspaces/roadmap/reports/
└── review-consolidated-2026-01-24-143000.yaml
    ├── SSOT verification (NEW v5.1)
    ├── Gap inventory
    ├── Stubs found
    ├── All 9 agent findings (prioritized)
    └── Remediation roadmap
```

**For Targeted Reviews:**
```
_workspaces/roadmap/issues/{DATE}/
├── review-ssot-verification.yaml      (Phase -1 - NEW)
├── review-gap-inventory.yaml          (Phase 1)
├── review-stubs.yaml                  (Phase 2)
├── Findings-SSOT.yaml                 (Agent 0 - NEW)
├── Findings-BRIT.yaml                 (Agent 1)
├── Findings-HALL.yaml                 (Agent 2)
├── Findings-GOV.yaml                  (Agent 3)
├── Findings-ASM.yaml                  (Agent 4)
├── Findings-DEBT.yaml                 (Agent 5)
├── Findings-STATE.yaml                (Agent 6)
├── Findings-ARCH.yaml                 (Agent 7)
├── Findings-INTEG.yaml                (Agent 8 - ENHANCED)
└── remediation-plan.yaml              (Phase 4)
```

---

## 🎯 Issue Severity: What It Means

| Level | Badge | When to Fix | Examples |
|-------|-------|------------|----------|
| **CRITICAL** 🔴 | Stop the line | Right now | Security breach, spec divergence >10%, integration gaps, unhandled crashes |
| **HIGH** 🟠 | Before next release | This sprint | Missing validation, race condition, CORE violation, MCP tool gap |
| **MEDIUM** 🟡 | This quarter | Next few weeks | Code duplication, missing docstring, design issue, incomplete wiring |
| **LOW** 🔵 | When you can | Next month | Style issue, minor refactoring, edge case handling |
| **INFO** ⚪ | FYI only | No deadline | Observation, pattern note, future consideration |

---

## ✅ Before You Ask for a Review

**Pre-Review Checklist:**
- ✅ You know what you want to check (full system? specific file? one agent?)
- ✅ You have ~90 minutes free (or less for targeted reviews, now 30 min for SSOT-only)
- ✅ You're ready to act on findings (create issues, plan fixes)
- ✅ The system is in a good state (tests running, no emergency)

**Quick Launch Requests:**
```
"Run a full code review"           → All 9 agents, 90 min
"Check SSOT alignment"             → Agent 0 only, 10 min
"Review MCP integration"           → Agent 8 expanded, 15 min
"Quick health check (25 minutes)"  → SSOT, BRIT, GOV, DEBT
```

---

## 🎓 Key Changes in v5.1

| What's New | Why | Impact |
|-----------|-----|--------|
| **Agent 0: SSOT-Compliance** | Catches spec divergence before other reviews | Prevents false "100% ready" claims |
| **Phase -1: SSOT Verification** | Runs before Phase 0, gates other reviews | Blocks circular patterns immediately |
| **Expanded INTEG Agent** | MCP tools, wiring, CLI, spec alignment | Catches integration gaps that were missed |
| **Enhanced Gap Inventory** | Detects integration gaps, not just stubs | Finds "written but not integrated" code |
| **Specification alignment report** | New consolidation output | Tracks spec vs impl over time |

---

## 🔗 Advanced: How Reviews Work Under the Hood

### Review Orchestrator
```python
from cortex.orchestrators.review.review_orchestrator import ReviewOrchestrator

reviewer = ReviewOrchestrator()
results = reviewer.full_review(scope="cortex/", include_ssot_verification=True)
```

### SSOT Verification (NEW)
```python
from cortex.review.ssot_compliance import SSOTComplianceAgent

ssot = SSOTComplianceAgent()
verification = ssot.verify_specification_alignment(
    prompt_files=["CORTEX.prompt.md", "cortex-review.prompt.md"],
    implementation_map="cortex-impl-map.yaml",
    tolerance_threshold=0.05  # 5% divergence threshold
)
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
logger.log_operation_start(operation="REVIEW_WITH_SSOT", scope="cortex/")
```

---

## 📋 Example: What You'll See (v5.1)

```markdown
## 🧠 CORTEX Review Results (v5.1)
**Date:** 2026-01-24 | **Scope:** cortex/ + cortex_brain/ | **Time:** 90 minutes

---

### PHASE -1: SSOT VERIFICATION RESULTS

🔑 **Specification Alignment Check**

| Component | Claimed | Actual | Divergence | Status |
|-----------|---------|--------|-----------|--------|
| Orchestrators Wired | 20/23 (87%) | 3/23 (13%) | 74% | 🔴 CRITICAL |
| MCP Tools Exposed | 15/15 | 5/23 | 67% | 🔴 CRITICAL |
| Test Pass Rate | 100% | 73% | 27% | 🔴 CRITICAL |
| Phase 1 Blocking | COMPLETE | INCOMPLETE | 100% | 🔴 CRITICAL |

**Result: 🔴 CRITICAL DIVERGENCE DETECTED**
Specification divergence exceeds 10% threshold on 4 metrics.
SSOT Verification FAILED - recommend specification update FIRST.

---

### Executive Summary
- **Total Issues:** 28 findings
- **Critical:** 5 (spec divergence + integration gaps)
- **High:** 10 (code quality + wiring issues)
- **Medium:** 10 (tech debt + design)
- **Low:** 3 (style + documentation)

---

### By Agent

| Agent | Issues | Critical | High | Medium | Low |
|-------|--------|----------|------|--------|-----|
| SSOT-Compliance | 4 | 4 | 0 | 0 | 0 |
| Brittleness | 3 | 0 | 1 | 2 | 0 |
| Hallucination | 2 | 0 | 1 | 0 | 0 |
| Governance | 5 | 0 | 2 | 3 | 0 |
| Assumptions | 4 | 0 | 0 | 3 | 1 |
| Debt | 3 | 0 | 1 | 2 | 0 |
| State | 1 | 0 | 1 | 0 | 0 |
| Architecture | 2 | 0 | 1 | 1 | 0 |
| Integration | 4 | 1 | 3 | 0 | 0 |

---

### 🔴 CRITICAL: Specification Divergence (SSOT-001 through SSOT-004)

**SSOT-001: Orchestrator Wiring Gap**
- Claimed: 20/23 (87%)
- Actual: 3/23 (13%)
- Root Cause: WIRE-001/002/003 written but not integrated

**SSOT-002: MCP Tool Exposure Gap**
- Claimed: 15 tools active
- Actual: 5/23 orchestrators expose tools
- Root Cause: get_mcp_tools() on only 5 orchestrators

**SSOT-003: Test Suite Metrics Inaccurate**
- Claimed: 100% pass rate
- Actual: 73% pass rate (5,500/7,547 tests)
- Root Cause: Tests not re-verified after infrastructure changes

**SSOT-004: Phase 1 Blocking Work Not Surfaced**
- Claimed: Phase 1 COMPLETE
- Actual: Phase 1 wiring integration incomplete
- Root Cause: WIRE modules written, not integrated

---

### 🟠 HIGH: MCP Integration Gap (INTEG-001 through INTEG-003)

**INTEG-001: MCP Tool Exposure Incomplete**
- 15 tools defined, 5/23 orchestrators expose them
- Missing: 18 orchestrators need get_mcp_tools()
- MCPServer integration incomplete

**INTEG-002: Orchestrator Wiring Not Integrated**
- WIRE-001/002/003 modules exist as standalones
- Not called from MasterOrchestrator.initialize()
- Auto-discovery (CORE-031) not wired

**INTEG-003: CLI Entry Points Missing**
- 5 CLI shortcuts promised
- 0 CLI shortcuts implemented
- No wiring to orchestrator execution
```

---

## ✅ Mandatory Before Production Deployment

**Review findings must report:**

```
✅ PHASE -1 (SSOT VERIFICATION):
   - All metrics verified against code
   - Specification divergence < 5%
   - No blocking integration gaps identified
   - All COMPLETE phases verified complete

✅ PHASE 1 (GAP INVENTORY):
   - WIRE modules: integrated (not just written)
   - MCP tools: all 23 orchestrators expose tools
   - CLI shortcuts: all 5 implemented
   - Specification: matches implementation

✅ AGENTS 1-8 (FULL REVIEW):
   - No CRITICAL code quality issues
   - No CRITICAL security/safety issues
   - No CRITICAL governance violations
   
Result: ✅ PRODUCTION READY for deployment
```

---

## 📞 Support

**SSOT Verification Issues:** Check `REVIEW_SYSTEM_ROOT_CAUSE_ANALYSIS.md` in `_workspaces/roadmap/`

**Questions about new Agent 0?** See `review-ssot-verification.yaml` output

**MCP Integration findings?** Check `Findings-INTEG.yaml` for detailed breakdown

---

**v5.1 - ENHANCED WITH SSOT-COMPLIANCE VERIFICATION**  
*Ensures specification integrity is gated BEFORE other reviews*
