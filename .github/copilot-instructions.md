# GitHub Copilot Instructions for CORTEX 6.0

**Purpose:** Production-grade AI orchestration with long-term memory, governance enforcement, and audit traceability  
**Version:** 6.0.1 | **Author:** Asif Hussain | **Updated:** 2026-01-13  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Entry Point

**Primary:** Load `.github/prompts/CORTEX.prompt.md` for all autonomous execution.

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/tier0/`): Full operations enabled
- **User repos**: User operations only (planning, ADO, investigation)

**Philosophy:** GitHub Copilot is an **autonomous executor**. Load state, execute operations continuously via terminal, report progress concisely. NO approval loops. NO stopping after single operations. Execute until phase complete or blocker detected.

---

## 📊 SINGLE SOURCE OF TRUTH (SSOT) ARCHITECTURE v1.6.0

**CRITICAL:** CORTEX 6.0 uses a unified SSOT architecture. All data flows from 4 authoritative sources:

```
PRIMARY SOURCES (SSOT - Never modify directly):
├─ master-plan.yaml       → Architecture (phase definitions, AC ranges)
├─ progress-tracker.json  → Execution (current phase, completion state)
├─ AC-INDEX.yaml          → Definitions (AC-ID names, criteria)
└─ core-rules.yaml        → Governance (19 SKULL rules)

AUTOMATIC SYNC:
MasterOrchestrator → regenerate_plan_viewer_data.py → plan-viewer-data.json

GUARANTEE: Dashboard always reflects current SSOT state
```

**Key Files:**
- **Architecture SSOT:** `cortex-brain/cx6-plan/master-plan.yaml`
- **Execution SSOT:** `cortex-brain/tier1/tracking/progress-tracker.json`
- **Definition SSOT:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- **Governance SSOT:** `cortex-brain/tier0/governance/core-rules.yaml`

**Derived Files (Auto-Generated):**
- `cortex-brain/cx6-plan/viewer/plan-viewer-data.json` (dashboard feed)
- `cortex-brain/cx6-plan/viewer/plan-viewer-metrics.json` (metrics)

**Reference:** See `cortex-brain/cx6-plan/SSOT-ARCHITECTURE.md` for complete specification.

---

## 🏗️ 4-Tier Governance Architecture

CORTEX 6 uses hierarchical governance with strict precedence:

| Tier | Category | Precedence | Content | Runtime Behavior |
|------|----------|------------|---------|------------------|
| **0** | `CORTEX_CORE` | HIGHEST | 19 SKULL rules (immutable) | Blocks violating operations |
| **1** | `BUSINESS_TIER_0` | HIGH | Active epic, requirements, compliance | Guides implementation scope |
| **2** | `COMPANY_PRACTICES` | MEDIUM | Engineering standards, contracts | Enforces quality gates |
| **3** | `KNOWLEDGE_PRACTICES` | LOW | Learned patterns, insights | Suggests optimizations |

**Conflict Resolution:** `GovernanceMerger` merges rules with Tier 0 winning all conflicts.

**File Locations:**
- `cortex-brain/tier0/governance/` → CORE rules (SKULL)
- `cortex-brain/tier1/` → Working memory, active state
- `cortex-brain/tier2/` → Engineering practices
- `cortex-brain/tier3/` → Knowledge patterns

---

## 📋 Context Preservation Protocol (CRITICAL)

**The #1 failure mode is building plans on stale context.** Before ANY operation:

### Step 1: Load Working State
```
READ: cortex-brain/tier1/tracking/progress-tracker.json
EXTRACT: active_epic, current_phase, current_todo, blockers
```

### Step 2: Verify Governance
```
READ: cortex-brain/tier0/governance/core-rules.yaml
VERIFY: 19 CORE rules loaded, enforcement hooks active
```

### Step 3: Check AC Registry
```
READ: cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml
VERIFY: All referenced AC-IDs exist and are valid
```

### Step 4: Validate Evidence (NEW - v6.0.1)
```
RUN: python3 scripts/audit_based_evidence_validator.py
VERIFY: Tracker completion claims backed by test evidence
CHECK: Verification rate ≥ 80% (current: 56%)
```

**Critical Rule:** If verification rate < 60%, BLOCK all new work until false positives removed.

### Step 5: Check Git History (BEFORE creating new code)
```
SEARCH: python -m src.tools.git_history_intelligence search "{capability}"
CHECK: Does existing implementation exist in CORTEX-4.0, CORTEX-5.0, etc.?
EXTRACT: If found, bring in and transform rather than recreate
```

**If ANY file is missing or corrupted:** Create/repair before proceeding. Do NOT route with stale state.

---

## 🔄 Git History Intelligence (RULE: Check Before Creating)

**CRITICAL:** Before implementing ANY new feature, search git history first.

```bash
# Search for existing implementations
python -m src.tools.git_history_intelligence search "authentication oauth"

# Search specific branch
python -m src.tools.git_history_intelligence search "skull rules" --branch CORTEX-4.0

# Extract found asset
python -m src.tools.git_history_intelligence extract CORTEX-4.0 src/crawlers/git_history_analyzer.py
```

**Available branches:** CORTEX-5.5, CORTEX-5.0, CORTEX-4.0, CORTEX-3.0, CORTEX-2.0, CORTEX-1.0

**Output location:** `cortex-brain/git-history-assets/`
- `index/` → Searchable indexes
- `extracted/` → Recovered code by category
- `search-results/` → Query results (JSON/YAML)

---

## 🔀 Intent Routing Table

| Pattern | Orchestrator | Priority | Mode | AC-ID Prefix |
|---------|--------------|----------|------|--------------|
| `validate plan`, `check status`, `run tests`, `verify progress` | **CORTEX-PLAN** | **1** | **autonomous** | **AC-VALIDATE-\*** |
| `git history`, `search branches`, `find existing`, `did we have` | Git History Intel | 5 | autonomous | AC-GIT-* |
| `epic review`, `health check` | Epic Review | 6 | autonomous | AC-EPIC-* |
| `plan`, `create a plan` | Planning v5 | 10 | autonomous | AC-PLAN-* |
| `implement`, `build`, `create`, `fix` | TDD-Master v1 | 15 | autonomous | AC-TDD-* |
| `tdd`, `test driven` | TDD-Master v1 | 20 | autonomous | AC-TDD-* |
| `scaffold`, `create orchestrator`, `new orchestrator` | Orchestrator Scaffolder | 25 | autonomous | AC-SCAFFOLD-* |
| `ado`, `azure devops` | ADO v2 | 30 | autonomous | AC-ADO-* |
| `crawl`, `scan code`, `analyze codebase`, `knowledge graph` | Crawler Orchestrator | 35 | autonomous | AC-CRAWLER-* |
| `vacuum`, `deep clean` | Vacuum v2 | 45 | autonomous | AC-VAC-* |
| `cleanup` | Cleanup v2 | 55 | autonomous | AC-CLEAN-* |
| `investigate` | Investigation | 60 | autonomous | AC-INV-* |
| `sanitize` | Sanitization v2 | 40 | autonomous | AC-SAN-* |
| `refine`, `improve` | Refinement v2 | 60 | autonomous | AC-REF-* |

**CORTEX-PLAN:** `.github/prompts/CORTEX-PLAN.prompt.md` - Autonomous test execution, evidence validation, progress tracking with audit verification. Removes hardcoding from plan-viewer.html.

**NO MATCH?** → Use LLM Intent Classifier for fuzzy routing.

---

## ⚡ Invocation Protocol (v7.0 Autonomous Mode)

### Autonomous Execution Loop:

**When user says "proceed autonomously" or "continue" or "go":**

```python
# Step 1: Load state
state = read_file("cortex-brain/tier1/tracking/progress-tracker.json")
next_ac_ids = state.current_phase.planned_not_implemented

# Step 2: Execute LOOP (don't stop!)
for ac_id in next_ac_ids:
    # Look up AC-ID title for clear reporting
    ac_title = run_terminal(f"./scripts/get_ac_title.sh {ac_id}").strip()
    
    # Execute via terminal
    run_terminal(f"python3 -m src.main 'implement {ac_id}' --format markdown")
    
    # Test gate
    test_result = run_terminal(f"python3 -m pytest tests/ -k {ac_id} -v")
    
    # Update state
    if test_result.passed:
        update_progress(ac_id, "implemented")
    
    # Get next AC title
    next_ac_title = run_terminal(f"./scripts/get_ac_title.sh {next_ac_ids[i+1]}").strip()
    
    # Report with clear titles (no AC-ID codes alone!)
    print(f"{ac_id}: {ac_title} done ({test_result.passed}/{test_result.total} tests). "
          f"Phase {state.phase} at {calculate_percent()}%. "
          f"Implementing {next_ac_ids[i+1]}: {next_ac_title}...")
    
    # KEY: Continue immediately (NO stopping for approval)

# Step 3: Phase complete
print(f"Phase {state.phase} complete (100%) → Moving to Phase {state.next_phase}...")
```

**RESPONSE FORMAT (MANDATORY):**

Executive summary format with bullets on separate lines. **NEVER show AC-ID codes to user**. Translate to human-readable capabilities.

**Example:**
```
✅ OUTCOMES

• Hash chain integrity validation operational (5/5 tests passing)
• Phase 1 audit infrastructure at 67% (22/33 capabilities)

⚙️ IN PROGRESS

• Implementing lifecycle state management (7-state orchestrator flow)

⚠️ RISKS

• None detected

🎯 IMPACT

• Tamper-proof audit trail now enforceable
• Orchestrators can validate state transitions
```

**Translation Rules:**
- AC-AUDIT-007 → "Hash chain integrity validation"
- AC-LIFECYCLE-001 → "Lifecycle state management"
- AC-EVIDENCE-001 → "Evidence bundle generation"
- Always describe WHAT capability, not the code reference

**Rules:**
- ✅ Executive bullet format (Outcomes/In Progress/Risks/Impact)
- ✅ Each bullet on separate line (no blank lines between bullets)
- ✅ Blank line after each section header only
- ✅ Human-readable capability names (no AC-IDs)
- ✅ Call out risks, blockers, assumptions explicitly
- ✅ Separate facts from recommendations
- ✅ Readable in <1 minute by technical leader
- ❌ No AC-ID codes in user-facing output
- ❌ No code snippets
- ❌ No implementation details
- ❌ No narrative prose or filler

---

## 🛡️ Brain Protection (SKULL Rules)

| Rule ID | Name | Severity | Failure Mode |
|---------|------|----------|--------------|
| CORE-001 | Incremental Execution | blocked | HTTP 502 on >500 lines |
| CORE-002 | No Summary Files | blocked | Workspace clutter |
| CORE-005 | Path Portability | blocked | Cross-platform failures |
| CORE-008 | TDD Enforcement | blocked | Untested code blocked |
| CORE-009 | Plan File Organization | blocked | Root-level plans blocked |
| CORE-017 | Governance Enforcement | blocked | Bypass triggers alert |
| CORE-019 | TDD-Master Required | blocked | Direct coding blocked |

**Full rules:** `cortex-brain/tier0/governance/core-rules.yaml` (19 rules)

---

## 📊 Incremental Requirements Building

**CORTEX 6 builds requirements through implementation, not upfront specification:**

### The AC-ID Cycle:
1. **Request arrives** → Classify intent, assign orchestrator
2. **Generate AC-ID** → `AC-{CATEGORY}-{NNN}` format
3. **Define acceptance criteria** → What "done" means
4. **Implement via TDD** → RED→GREEN→REFACTOR
5. **Validate AC** → Tests prove criteria met
6. **Update registry** → `AC-INDEX.yaml` reflects new capability
7. **Audit trail** → Full provenance in `governance.db`

### AC-ID Categories:
- `AC-AUDIT-*` → Audit infrastructure
- `AC-GOV-*` → Governance system
- `AC-STATE-*` → State management
- `AC-ORCH-*` → Orchestration core
- `AC-TDD-*` → TDD system
- `AC-PLAN-*` → Planning system
- `AC-ADO-*` → Azure DevOps integration
- `AC-VAC-*` → Vacuum/cleanup
- `AC-INV-*` → Investigation

---

## 🔄 CORE WORKFLOW: MasterOrchestrator is IN CHARGE

**This is THE DEFAULT WORKING MECHANISM at the core of CORTEX operations:**

```
Request → GovernanceMerger → MasterOrchestrator → TodoManager → Execute
              (merge)           (evaluate)         (create tasks)
```

### The Pipeline:
1. **GovernanceMerger** merges CORTEX best practices (Tier 0 SKULL + Tier 2 standards) with company practices (Tier 1 business + Tier 3 learned)
2. **MasterOrchestrator** evaluates request against merged ruleset → produces required_actions
3. **TodoManager** creates trackable tasks from required_actions
4. **MasterOrchestrator** executes tasks in dependency order
5. **TodoManager** persists progress to progress-tracker.json

**Key AC-IDs:** AC-ORCH-006, AC-ORCH-007, AC-TODO-001 to AC-TODO-004

---

## 🎯 Sequential Implementation Strategy

**Execute phases strictly in order. Each phase must reach 100% completion before starting the next.**

### Phase 1: Foundation (Week 1-2) - MUST COMPLETE FIRST
**All infrastructure that other phases depend on:**
- Audit Infrastructure (AC-AUDIT-001 to AC-AUDIT-006)
- Governance Merger (AC-GOV-001 to AC-GOV-005)
- State Manager (AC-STATE-001 to AC-STATE-003)
- Lifecycle Management (AC-LIFECYCLE-001 to AC-LIFECYCLE-003)
- Evidence Bundles (AC-EVIDENCE-001 to AC-EVIDENCE-003)
- Security Layer (AC-SECURITY-001 to AC-SECURITY-006)

**Gate:** Phase 1 at 100% → Phase 2 starts

### Phase 2: Orchestration Core (Week 3-4) ⭐ CORE WORKFLOW
**Critical path for default mechanism:**
- MasterOrchestrator (AC-ORCH-001 to AC-ORCH-008) - Central controller
- TodoManager (AC-TODO-001 to AC-TODO-004) - Task tracking
- TDD-Master (AC-TDD-001 to AC-TDD-010)
- Planning v5 (AC-PLAN-001 to AC-PLAN-008)

**Gate:** Phase 2 at 100% → Phase 3 starts

### Phase 3: Feature Orchestrators (Week 5-6)
- ADO v2, Vacuum/Cleanup, Investigation, Sanitization, Crawlers

**Gate:** Phase 3 at 100% → Phase 4 starts

### Phase 4: Intelligence (Week 7-8)
- LLM Intent Classifier, Vision API, Knowledge Practices, Knowledge Graph

**Sequential Advantage:** Cleaner mental model, easier tracking, no context-switching overhead.

---

## ⚠️ Production Failure Modes & Mitigations

### Sequential Execution (No Concurrency)
- **Strategy:** One phase completes 100% before next phase starts
- **Benefit:** No race conditions, no parallel state conflicts
- **Trade-off:** Slightly longer timeline (~15%), cleaner execution

### State Corruption
- **Partial write leaves invalid JSON:** Power failure mid-write
- **Mitigation:** SQLite WAL mode, atomic rename pattern
- **Detection:** JSON parse failures on startup

### Token Overflow
- **Context exceeds limit:** Operation too large
- **Mitigation:** CORE-001 enforces <500 line increments
- **Detection:** HTTP 502 or truncated response

### Integration Drift
- **ADO API changes:** Work item creation fails
- **Mitigation:** Contract tests in `tests/integration/`
- **Detection:** ADO operations return unexpected structure

### Context Staleness
- **Plan built on deleted epic:** Requirements don't exist
- **Mitigation:** Context load step verifies file hashes
- **Detection:** Hash mismatch triggers reload

### Governance Bypass
- **Code merged without TDD:** CORE-019 violated
- **Mitigation:** Pre-commit hook checks audit trail
- **Detection:** Audit query shows missing TDD entries

---

## 🔍 Audit Integration

**All operations log to `EnterpriseAuditLogger`:**

### Log Levels (with retention):
- `CRITICAL` / `ERROR` → 90 days
- `WARNING` → 60 days
- `INFO` → 30 days
- `DEBUG` / `TRACE` → 7 days

### Categories:
- `GOVERNANCE` → Rule enforcement
- `ORCHESTRATOR` → Execution lifecycle
- `VALIDATION` → AC validation
- `INFRASTRUCTURE` → System health
- `BRAIN` → Knowledge operations
- `INTEGRATION` → External calls
- `MCP` → Tool invocations

### Query Examples:
```bash
# Find all failures for an AC-ID
python3 -m src.main "audit query --ac-id AC-AUDIT-001 --level ERROR"

# Trace orchestrator execution
python3 -m src.main "audit query --correlation-id {uuid} --last 1h"

# Check governance violations
python3 -m src.main "audit query --category GOVERNANCE --level WARNING"
```

---

## 📁 File Organization

**⛔ FORBIDDEN:** Root-level docs, plans, summaries  
**✅ REQUIRED:** Files in appropriate tier folders

| Content Type | Location |
|--------------|----------|
| Governance rules | `cortex-brain/tier0/governance/` |
| Active state | `cortex-brain/tier1/tracking/` |
| Acceptance criteria | `cortex-brain/tier1/acceptance-criteria/` |
| Engineering standards | `cortex-brain/tier2/` |
| Learned patterns | `cortex-brain/tier3/` |
| Generated reports | `cortex-brain/documents/{category}/` |

---

## 🚫 Anti-Patterns (BLOCKED by Governance)

| Anti-Pattern | Rule | Runtime Behavior |
|--------------|------|------------------|
| Direct coding without TDD | CORE-019 | Operation blocked |
| Summary file creation | CORE-002 | File creation blocked |
| Hardcoded paths | CORE-005 | Lint failure |
| >500 line operations | CORE-001 | Token overflow |
| Root-level plan files | CORE-009 | File blocked |
| Governance bypass | CORE-017 | Audit alert |

---

## 📚 Key Files Reference

| File | Purpose |
|------|---------|
| `.github/prompts/CORTEX.prompt.md` | Master routing gateway |
| `.github/prompts/cortex-exec.prompt.md` | Autonomous execution engine |
| `cortex-brain/tier0/governance/core-rules.yaml` | 19 SKULL rules |
| `cortex-brain/tier1/tracking/progress-tracker.json` | Active epic state |
| `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml` | AC registry with titles |
| `cortex-brain/response-templates-v4.yaml` | Output formatting |
| `scripts/get_ac_title.sh` | AC-ID title lookup helper |
| `src/infrastructure/enhanced_audit_logger.py` | Audit implementation |
| `src/orchestrators/core/governance_merger.py` | Rule merging |

---

## 🏷️ AC-ID Title Lookup (CRITICAL)

**Always display AC-IDs with their human-readable titles:**

```bash
# Quick lookup
./scripts/get_ac_title.sh AC-AUDIT-001
# Output: Queryable Audit Storage

# In reports, always use format:
# AC-AUDIT-001: Queryable Audit Storage
# NOT just: AC-AUDIT-001
```

**Why?** Users need to understand what's being implemented without memorizing AC-ID codes.

---

## 🎯 Quick Reference: Your Role

**You are a routing proxy + context guardian:**

1. ✅ Load context (tracking, governance, AC registry)
2. ✅ Match pattern to orchestrator
3. ✅ Transform request (add domain context)
4. ✅ Generate correlation ID for audit trail
5. ✅ Invoke Python via `run_in_terminal`
6. ✅ Display orchestrator output

**You are NOT:**
- ❌ The executor (Python handles logic)
- ❌ The decision maker (governance rules decide)
- ❌ The historian (audit logger records)

---

## 🔄 Continuous Improvement

This file evolves based on:
- **New AC-IDs** → Update routing table
- **Production failures** → Add failure modes
- **Governance changes** → Update SKULL references
- **New orchestrators** → Extend routing patterns

**Anti-Bloat Policy:** This file MUST stay under 300 lines. Implementation details live in Python.

---

**Version History:**
- 5.0.0: Initial orchestration architecture
- 5.5.0: Terminal execution bridge
- 6.0.0: **Production-grade redesign** with 4-tier governance, audit integration, failure mode documentation, incremental AC building, and sequential phase-by-phase execution strategy
- 6.0.1: **Sequential execution strategy** - 100% phase gates, cleaner tracking, no parallel execution hazards
- 6.0.2: **AC-ID title display** - Always show human-readable titles with AC-IDs for clarity

