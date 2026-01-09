# 🔍🔧 CORTEX Gap-Fix - Holistic Gap Detection & Remediation

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Analysis + Remediation  
**Author:** Asif Hussain | **AC Reference:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**UNIFIED GAP DETECTION + REMEDIATION** - Combines search and alignment in one autonomous pipeline:

1. **🔍 SEARCH (Phases 0-4):** Discover gaps, violations, brittleness, audit issues
2. **🔧 ALIGN (Phases 5-11):** Prioritize, remediate, sync plans with snowball ordering

**⚠️ CRITICAL: This is FULLY AUTONOMOUS - executes all 12 phases without user confirmation.**

---

## 🔀 Intent Routing

**Patterns:**
- `^(gap-fix|gapfix|search and align|find and fix|detect and remediate).*$`
- `^(full gap analysis|end-to-end alignment|comprehensive fix).*$`

**Priority:** 7 (Critical - Discovery + Remediation)  
**Mode:** Autonomous  
**Confidence:** 1.0

---

## 📊 Visual Progress Tracker Template

**Show at EACH phase transition:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               🔍🔧 CORTEX GAP-FIX - DETECTION & REMEDIATION                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overall Progress: `████████░░░░░░░░░░░░` 40% 🔄 IN PROGRESS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ ─────────────────── 🔍 SEARCH PHASE ───────────────────                     │
│ Phase 0  - AC Document Loading    `██████████` 100% ✅ Complete             │
│ Phase 1  - Implementation Scan    `██████████` 100% ✅ Complete             │
│ Phase 2  - Discrepancy Detection  `██████████` 100% ✅ Complete             │
│ Phase 3  - Violation Scan         `████████░░`  80% 🔄 In Progress          │
│ Phase 4  - Audit Gap Analysis     `░░░░░░░░░░`   0% ⏳ Pending              │
├─────────────────────────────────────────────────────────────────────────────┤
│ ─────────────────── 🔧 ALIGN PHASE ───────────────────                      │
│ Phase 5  - MCP Validation         `░░░░░░░░░░`   0% ⏳ Pending              │
│ Phase 6  - Load Findings          `░░░░░░░░░░`   0% ⏳ Pending              │
│ Phase 7  - Categorize             `░░░░░░░░░░`   0% ⏳ Pending              │
│ Phase 8  - Snowball Sort          `░░░░░░░░░░`   0% ⏳ Pending              │
│ Phase 9  - Plan Generation        `░░░░░░░░░░`   0% ⏳ Pending              │
│ Phase 10 - Plan Integration       `░░░░░░░░░░`   0% ⏳ Pending              │
│ Phase 11 - Holistic Plan Sync     `░░░░░░░░░░`   0% ⏳ Pending              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⛔ FORBIDDEN Behaviors

**❌ NEVER DO THESE:**
- Ask "Should I proceed?" or "Do you want me to continue?"
- Wait for user confirmation before starting next phase
- Output "Ready for next phase?" messages
- Pause execution after analysis
- Generate partial reports and stop

**✅ ALWAYS DO THESE:**
- Execute ALL 12 phases in sequence automatically
- Show visual progress tracker at phase transitions
- Generate final consolidated report at Phase 11 completion
- Proceed to next phase immediately after current phase completes

---

# 🔍 SEARCH PIPELINE (Phases 0-4)

## 📋 Analysis Categories

### Category 1: AC Implementation Gaps
**Source of Truth:** `00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`

| AC Section | Risk Level | Criteria Count |
|------------|------------|----------------|
| `governance_compliance` (AC-GOV-*) | 🔴 CRITICAL | 10 |
| `architecture_cleanliness` (AC-ARCH-*) | 🔴 CRITICAL | 5 |
| `foundation_layer` (AC-F01-*) | 🔴 CRITICAL | 6 |
| `todo_orchestrator` (AC-F02-*) | 🔴 CRITICAL | 7 |
| `orchestrator_capabilities` (AC-ORC-*) | 🟠 HIGH | 10+ |
| `plan_viewer_dashboard` (AC-PLAN-DASH-*) | 🔴 CRITICAL | 7 |
| `concurrency_safety` (AC-RACE-*) | 🔴 CRITICAL | 3 |
| `security_compliance` (AC-SEC-*) | 🔴 CRITICAL | 8 |
| `multi_repo_registry` (AC-REPO-*) | 🔴 CRITICAL | 5 |
| `learning_library` (AC-LEARN-*) | 🟠 HIGH | 5 |

### Category 2: SKULL Rule Violations

| Rule | Detection Pattern | Severity |
|------|-------------------|----------|
| TDD_ENFORCEMENT | Code without failing test first | 🔴 BLOCKED |
| HOLISTIC_DISCOVERY | File creation without workspace search | 🔴 BLOCKED |
| GIT_ISOLATION | CORTEX commits to user repos | 🔴 BLOCKED |
| PLANNING_ISOLATION | Plans implement code | 🔴 BLOCKED |
| YAML_SAFE_LOADER | `yaml.load()` without SafeLoader | 🔴 CRITICAL |

### Category 3: Architecture Anti-Patterns

| Anti-Pattern | Detection Regex | Risk |
|--------------|-----------------|------|
| Hardcoded paths | `hardcoded.*=.*["\']\/` | 🔴 HIGH |
| Direct file writes | `open\([^,]+,\s*["\']w` | 🟠 MEDIUM |
| Bare except | `except\s*:` | 🟠 HIGH |
| Type ignore | `# type:\s*ignore` | 🟡 MEDIUM |

### Category 4: Security Vulnerabilities

| Vulnerability | Detection Pattern | Risk |
|---------------|-------------------|------|
| Code injection | `eval\(|exec\(` | 🔴 CRITICAL |
| Shell injection | `subprocess.*shell=True` | 🔴 CRITICAL |
| Hardcoded secrets | `password\s*=\s*["\']` | 🔴 CRITICAL |
| YAML injection | `yaml\.load\(` | 🔴 CRITICAL |

---

### Phase 0: AC Document Loading
**Duration:** <10 seconds

**Actions:**
1. Load `00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`
2. Parse all 370+ acceptance criteria
3. Build validation checklist by category
4. Identify blocking vs non-blocking criteria

**Phase Completion Output:**
```
✅ Phase 0 - AC Document Loading: Complete
   └─ Criteria Loaded: 374 | Categories: 15 | Blocking: 42
   └─ AC Version: 10.0.0
   └─ Duration: 3s
   └─ Auto-proceeding to Phase 1...
```

---

### Phase 1: Implementation Inventory
**Duration:** 2-3 minutes

**Scan Targets:**
```
src/orchestrators/       → Orchestrator implementations
src/cortex_agents/       → Agent implementations
src/database/            → StateManager, DAG
src/infrastructure/      → AuditLogger, utilities
tests/                   → Test coverage
cortex-brain/manifests/  → Orchestrator configs
cortex-brain/tier0/      → Governance rules
```

**Output:** Implementation matrix mapping AC → code

**Phase Completion Output:**
```
✅ Phase 1 - Implementation Scan: Complete
   └─ Files Scanned: {count} | Implementations Found: {count}
   └─ Coverage Matrix Generated
   └─ Duration: 120s
   └─ Auto-proceeding to Phase 2...
```

---

### Phase 2: Discrepancy Detection
**Duration:** 2-3 minutes

**Discrepancy Types:**
- **MISSING** - AC criterion exists, no code found
- **PARTIAL** - Code exists but incomplete
- **STALE** - Code outdated vs spec
- **CONFLICT** - Code differs from AC
- **OVER** - Code exceeds AC scope

**Phase Completion Output:**
```
✅ Phase 2 - Discrepancy Detection: Complete
   └─ Discrepancies Found: {count}
   └─ MISSING: {count} | PARTIAL: {count} | STALE: {count}
   └─ Duration: 90s
   └─ Auto-proceeding to Phase 3...
```

---

### Phase 3: Violation & Brittleness Scan
**Duration:** 2-3 minutes

**Scans for:**
- SKULL rule violations
- Architecture anti-patterns
- Security vulnerabilities
- Missing error handling
- Race condition risks
- Global state mutations

**Phase Completion Output:**
```
✅ Phase 3 - Violation Scan: Complete
   └─ Violations Found: {count} | Brittleness: {count}
   └─ Security Issues: {count} | Anti-Patterns: {count}
   └─ Duration: 90s
   └─ Auto-proceeding to Phase 4...
```

---

### Phase 4: Audit Gap Analysis & Findings Output
**Duration:** 1-2 minutes

**Per AC-INT-006:** Verify every criterion has audit log coverage

**Primary Output:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/search-findings-{timestamp}.yaml`

```yaml
search_findings:
  generated_at: '2026-01-09T10:30:00Z'
  ac_version: '10.0.0'
  ac_location: 'cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml'
  
  summary:
    total_issues: 78
    critical: 24
    high: 31
    medium: 18
    low: 5
    
  discrepancies:
    - id: AC-GOV-001
      type: PARTIAL
      description: "SKULL rule migration incomplete"
      evidence_found: ["cortex-brain/tier0/governance/"]
      evidence_missing: ["tests/governance/test_skull_migration.py"]
      severity: CRITICAL
      blocking: true
      
  violations:
    - rule: YAML_SAFE_LOADER
      file: "src/utils/config_loader.py"
      line: 45
      pattern: "yaml.load(f)"
      fix: "yaml.safe_load(f)"
      severity: CRITICAL
      
  brittleness:
    - type: RACE_CONDITION
      file: "src/database/state_manager.py"
      description: "Concurrent writes without locking"
      severity: CRITICAL
      
  audit_gaps:
    - criterion: AC-F02-006
      gap_type: NO_AUDIT_COVERAGE
      recommendation: "Add audit logging for TODO state integration"
```

**Phase Completion Output:**
```
✅ Phase 4 - Audit Gap Analysis: Complete
   └─ Audit Gaps: {count} | Findings File Generated
   └─ Output: search-findings-{timestamp}.yaml
   └─ Duration: 60s
   └─ 🔍 SEARCH COMPLETE → Auto-proceeding to ALIGN Phase 5...
```

---

# 🔧 ALIGN PIPELINE (Phases 5-11)

### Phase 5: MCP Tool Validation (Pre-Requisite)
**Duration:** <5 seconds | **BLOCKING:** Yes

**⚠️ CRITICAL: This phase MUST pass before Phase 11**

**Validation Checks:**
| Check | File/Location | Required |
|-------|---------------|----------|
| MCP Tool Implementation | `src/mcp/align_plan_sync.py` | ✅ REQUIRED |
| Capability Registration | `src/mcp/capability_registry.py` → `cortex_align_plan_sync` | ✅ REQUIRED |
| MCP Export | `src/mcp/__init__.py` → `AlignPlanSyncTool` | ✅ REQUIRED |

**Validation Command:**
```bash
python3 -c "from src.mcp.align_plan_sync import AlignPlanSyncTool; print('✅ MCP tool ready')"
```

**Phase Completion Output (Success):**
```
✅ Phase 5 - MCP Validation: Complete
   └─ Tool: cortex_align_plan_sync ✅ Found
   └─ Capability: Registered ✅
   └─ Duration: 2s
   └─ Auto-proceeding to Phase 6...
```

**Phase Output (Failure - NON-BLOCKING for Phases 6-10):**
```
⚠️ Phase 5 - MCP Validation: FAILED (Phase 11 will be blocked)
   └─ Tool: cortex_align_plan_sync ❌ NOT FOUND
   └─ Required File: src/mcp/align_plan_sync.py
   └─ Note: Phases 6-10 will proceed, Phase 11 blocked
   └─ Auto-proceeding to Phase 6...
```

---

### Phase 6: Load Search Findings
**Duration:** <10 seconds

**Actions:**
1. Load `search-findings-{timestamp}.yaml` from Phase 4
2. Parse all discrepancies, violations, brittleness, audit gaps
3. Validate findings structure
4. Count issues by severity

**Phase Completion Output:**
```
✅ Phase 6 - Load Findings: Complete
   └─ Issues Loaded: {count} | Critical: {count} | High: {count}
   └─ Duration: 3s
   └─ Auto-proceeding to Phase 7...
```

---

### Phase 7: Categorize & Analyze
**Duration:** 1-2 minutes

**Actions:**
1. Group issues by category (governance, architecture, security, etc.)
2. Identify blocking issues (must fix first)
3. Calculate downstream impact for each issue
4. Map issue dependencies

**Phase Completion Output:**
```
✅ Phase 7 - Categorize: Complete
   └─ Categories: 6 | Blocking Issues: {count} | Dependencies Mapped: {count}
   └─ Duration: 45s
   └─ Auto-proceeding to Phase 8...
```

---

### Phase 8: Snowball Prioritization
**Duration:** 1-2 minutes

**Snowball Algorithm:**
```python
def snowball_prioritize(issues):
    """
    Priority Order (fixes that unlock most downstream work first):
    1. BLOCKING criteria (prevent other work)
    2. Foundation fixes (unlock 3+ downstream fixes)
    3. Security vulnerabilities (risk mitigation)
    4. Race conditions (stability)
    5. Audit gaps (enable validation)
    6. Performance issues (SLA compliance)
    7. Code quality (maintainability)
    """
    layers = [
        ("🔴 Layer 1: Blocking Criteria", filter_blocking(issues)),
        ("🟠 Layer 2: Foundation Fixes", filter_foundation(issues)),
        ("🔴 Layer 3: Security", filter_security(issues)),
        ("🟠 Layer 4: Race Conditions", filter_concurrency(issues)),
        ("🟡 Layer 5: Audit Gaps", filter_audit(issues)),
        ("🟢 Layer 6: Performance", filter_performance(issues)),
        ("⚪ Layer 7: Quality", filter_quality(issues)),
    ]
    return flatten_with_order(layers)
```

**Phase Completion Output:**
```
✅ Phase 8 - Snowball Sort: Complete
   └─ Priority Layers: 7 | Snowball Impact Calculated
   └─ Layer 1 (Blocking): {count} issues → Unlocks {count} downstream
   └─ Duration: 30s
   └─ Auto-proceeding to Phase 9...
```

---

### Phase 9: Generate Remediation Plan
**Duration:** 2-3 minutes

**Pre-Step: Archive Existing Remediation**
```
🔄 Phase 9.0 - Archive Existing: Starting
   └─ Checking: {plan_path}/acceptance-criteria/remediation-plan.yaml
   └─ Found existing → Moving to archive/remediation-plan-{date}.yaml
   └─ Archive complete ✅
```

**Lifecycle Rules:**
| Rule | Description |
|------|-------------|
| **ARCHIVE_BEFORE_REGENERATE** | Move existing `remediation-plan.yaml` to `archive/` with timestamp |
| **SINGLE_ACTIVE_PLAN** | Only ONE `remediation-plan.yaml` exists (no timestamps in active) |
| **PRESERVE_HISTORY** | Never delete archived remediations (audit trail) |

**Plan Structure:**
```yaml
remediation_plan:
  generated_at: '2026-01-09T10:30:00Z'
  total_issues: 78
  blocking_issues: 24
  estimated_effort: "48 hours"
  
  phases:
    - phase: 1
      name: "Foundation Blockers"
      priority: "🔴 CRITICAL"
      issues:
        - id: AC-GOV-001
          description: "SKULL rule migration incomplete"
          effort: "2h"
          fix: "Migrate remaining rules to CORE-* numbering"
      estimated_hours: 8
      snowball_impact: "Unlocks 15 downstream criteria"
```

**Phase Completion Output:**
```
✅ Phase 9 - Plan Generation: Complete
   └─ Archived: remediation-plan-{date}.yaml
   └─ Plan Phases: 7 | Total Effort: {hours}h | Blocking Fixed: {count}
   └─ Output: remediation-plan.yaml
   └─ Duration: 90s
   └─ Auto-proceeding to Phase 10...
```

---

### Phase 10: Integrate with Feature Plan
**Duration:** 1-2 minutes

**Actions:**
1. Check for associated plan in `cortex-brain/documents/planning/active/`
2. If exists: Inject findings as new phase (position 0 for blockers)
3. Reorder existing phases for snowball effect
4. Update progress tracker JSON
5. Generate continuation prompt

**Phase Completion Output:**
```
✅ Phase 10 - Plan Integration: Complete
   └─ Plan Found: cortex6
   └─ New Phase Added: "Critical Blockers (Align)" at position 0
   └─ Tasks Added: {count} blocking + {count} high priority
   └─ Duration: 45s
   └─ Auto-proceeding to Phase 11...
```

---

### Phase 11: Holistic Plan Synchronization (MCP)
**Duration:** 2-5 minutes

**⚠️ CRITICAL: Requires Phase 5 MCP validation to have passed**

**Actions:**
1. **Invoke MCP Tool:** `cortex_align_plan_sync` via MCP server
2. **Holistic Review:** AC YAML + Remediation Plan + Snowball Strategy
3. **Plan Decision:** Create new or revise existing
4. **Snowball Optimization:** Reorder for maximum momentum
5. **Alignment Validation:** Ensure AC ↔ requirements.yaml ↔ plan are aligned

**Phase Completion Output:**
```
✅ Phase 11 - Holistic Plan Sync: Complete
   └─ Mode: {create|revise}
   └─ Plan Structure: {epic|feature}
   └─ Gaps Added: {count}
   └─ Snowball Optimized: ✅
   └─ AC ↔ Requirements ↔ Plan: ALIGNED
   └─ Duration: 120s
   └─ 🎉 ALL PHASES COMPLETE
```

---

## 📝 Final Report Template

**Generated ONLY after Phase 11 completion:**

```markdown
# 🔍🔧 CORTEX Gap-Fix Report

**Date:** {date}
**Duration:** {total_duration}
**Status:** ✅ ALL PHASES COMPLETE

---

## Visual Progress Tracker

┌─────────────────────────────────────────────────────────────────────────────┐
│               🔍🔧 CORTEX GAP-FIX - DETECTION & REMEDIATION                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overall Progress: `████████████████████` 100% ✅ COMPLETE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ ─────────────────── 🔍 SEARCH PHASE ───────────────────                     │
│ Phase 0  - AC Document Loading    `██████████` 100% ✅ Complete             │
│ Phase 1  - Implementation Scan    `██████████` 100% ✅ Complete             │
│ Phase 2  - Discrepancy Detection  `██████████` 100% ✅ Complete             │
│ Phase 3  - Violation Scan         `██████████` 100% ✅ Complete             │
│ Phase 4  - Audit Gap Analysis     `██████████` 100% ✅ Complete             │
├─────────────────────────────────────────────────────────────────────────────┤
│ ─────────────────── 🔧 ALIGN PHASE ───────────────────                      │
│ Phase 5  - MCP Validation         `██████████` 100% ✅ Complete             │
│ Phase 6  - Load Findings          `██████████` 100% ✅ Complete             │
│ Phase 7  - Categorize             `██████████` 100% ✅ Complete             │
│ Phase 8  - Snowball Sort          `██████████` 100% ✅ Complete             │
│ Phase 9  - Plan Generation        `██████████` 100% ✅ Complete             │
│ Phase 10 - Plan Integration       `██████████` 100% ✅ Complete             │
│ Phase 11 - Holistic Plan Sync     `██████████` 100% ✅ Complete             │
└─────────────────────────────────────────────────────────────────────────────┘

📊 **Issues Found:** {count} | **Remediated:** {count} | **Effort:** {hours}h

---

## Executive Summary

| Category | Total | Blocking | Effort |
|----------|-------|----------|--------|
| Governance | {count} | {blocking} | {hours}h |
| Architecture | {count} | {blocking} | {hours}h |
| Security | {count} | {blocking} | {hours}h |
| Concurrency | {count} | {blocking} | {hours}h |
| Audit Gaps | {count} | {blocking} | {hours}h |
| **TOTAL** | **{total}** | **{blocking_total}** | **{total_hours}h** |

---

## 🌊 Snowball Execution Order

**Phase 1:** Foundation Blockers ({hours}h) → Unlocks {count} criteria
**Phase 2:** Concurrency Safety ({hours}h) → Enables parallel testing
**Phase 3:** Audit Gaps ({hours}h) → Enables automated validation
**Phase 4:** Security ({hours}h) → Risk mitigation
**Phase 5:** Performance ({hours}h) → SLA compliance
**Phase 6:** Quality ({hours}h) → Maintainability

---

## 📁 Generated Artifacts

- `search-findings-{timestamp}.yaml` (findings)
- `remediation-plan.yaml` (active)
- `archive/remediation-plan-{date}.yaml` (previous)
- `snowball-strategy.yaml` (prioritization)
- `progress-tracker.json` (updated)

---

## 🚀 Next Steps

Execute the remediation plan:
```
/CORTEX continue cortex6
```

---

**Report Generated:** {timestamp}
```

---

## 📁 File Locations (Canonical)

| Artifact | Location |
|----------|----------|
| **AC Source of Truth** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml` |
| **Search Findings** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/search-findings-{timestamp}.yaml` |
| **Remediation Plan** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/remediation-plan.yaml` |
| **Snowball Strategy** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/snowball-strategy.yaml` |
| **Archive** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/archive/` |

---

## ⚡ Invocation

**Standard (full 12-phase pipeline):**
```
/CORTEX gap-fix
```

**With specific plan:**
```
/CORTEX gap-fix --plan cortex6
```

**With scope filter:**
```
/CORTEX gap-fix --scope governance
/CORTEX gap-fix --scope security
```

---

## 🛡️ Brain Protection Compliance

| SKULL Rule | Compliance |
|------------|------------|
| **HOLISTIC_DISCOVERY** | ✅ Searches entire workspace before changes |
| **PLANNING_ISOLATION** | ✅ Generates plans, does NOT implement fixes |
| **GIT_ISOLATION** | ✅ Only modifies CORTEX planning files |
| **ARCHIVE_BEFORE_REGENERATE** | ✅ Preserves remediation history |
| **MCP_ONLY_TOOL_ACCESS** | ✅ Phase 11 uses MCP for Python execution |

---

## 📚 References

- **Main Entry Point:** `.github/prompts/CORTEX.prompt.md`
- **AC Source:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`
- **MCP Server:** `src/mcp/align_plan_sync.py` (Phase 11 implementation)
- **Orchestrators Docs:** `cortex-brain/documents/orchestrators-quick-ref.md`

---

**Version History:**
- v1.0.0 (2026-01-09): Initial release - combined search + align into unified 12-phase pipeline

