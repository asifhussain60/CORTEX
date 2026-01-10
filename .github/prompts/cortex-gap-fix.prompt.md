# 🔍🔧 CORTEX Gap-Fix - Holistic Gap Detection & Remediation

**Version:** 1.5.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Analysis + Remediation  
**Author:** Asif Hussain | **Source of Truth:** CORTEX 6.0 Canonical Requirements  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**UNIFIED GAP DETECTION + REMEDIATION** - Keeps CORTEX 6.0 plan aligned with canonical sources:

1. **🔍 SEARCH (Phases 0-4):** Discover gaps vs CX6-requirements.yaml & CX6-acceptance-criteria.yaml
2. **🔧 ALIGN (Phases 5-11):** Prioritize, remediate, sync plans with snowball ordering
3. **🎯 VALIDATION:** Ensure active plan matches 18 SR requirements + 361 AC criteria

**⚠️ CRITICAL: This is FULLY AUTONOMOUS - executes all 12 phases without user confirmation.**

**🎯 Goal:** Maintain plan alignment with canonical sources during CORTEX 6.0 build (210-288h effort)

---

## 🔀 Intent Routing

**Patterns:**
- `^(gap-fix|gapfix|search and align|find and fix|detect and remediate).*$`
- `^(full gap analysis|end-to-end alignment|comprehensive fix).*$`

**Priority:** 7 (Critical - Discovery + Remediation)  
**Mode:** Autonomous  
**Confidence:** 1.0

---

## 📊 Visual Progress Display Standards

### Initial Display (Show ONCE at start)

**Full phase table shown only at pipeline start:**

| Overall | Progress | Status |
|---------|----------|--------|
| 🔍🔧 Gap-Fix | `░░░░░░░░░░` 0% | 🔄 Starting |

| Phase | Name | Status |
|-------|------|--------|
| 0 | AC Document Loading | ⏳ Pending |
| 1 | Implementation Scan | ⏳ Pending |
| 2 | Discrepancy Detection | ⏳ Pending |
| 3 | Violation Scan | ⏳ Pending |
| 4 | Audit Gap Analysis | ⏳ Pending |
| 5 | MCP Validation | ⏳ Pending |
| 6 | Load Findings | ⏳ Pending |
| 7 | Categorize | ⏳ Pending |
| 8 | Snowball Sort | ⏳ Pending |
| 9 | Plan Generation | ⏳ Pending |
| 10 | Plan Integration | ⏳ Pending |
| 10B | Conflict Validation | ⏳ Pending |
| 10C | Test Stability Validation | ⏳ Pending |
| 11 | Holistic Plan Sync | ⏳ Pending |

---

### During Execution (Minimal 3-Row Update)

**After each phase completion, show ONLY:**

| Overall | Completed | Next |
|---------|-----------|------|
| `████░░░░░░` 33% | ✅ Phase 3: Violation Scan | 🔄 Phase 4: Audit Gap Analysis |

---

### Final Display (Show complete table)

| Overall | Progress | Status |
|---------|----------|--------|
| 🔍🔧 Gap-Fix | `██████████` 100% | ✅ Complete |

| Phase | Name | Status |
|-------|------|--------|
| 0 | AC Document Loading | ✅ Complete |
| 1 | Implementation Scan | ✅ Complete |
| 2 | Discrepancy Detection | ✅ Complete |
| 3 | Violation Scan | ✅ Complete |
| 4 | Audit Gap Analysis | ✅ Complete |
| 5 | MCP Validation | ✅ Complete |
| 6 | Load Findings | ✅ Complete |
| 7 | Categorize | ✅ Complete |
| 8 | Snowball Sort | ✅ Complete |
| 9 | Plan Generation | ✅ Complete |
| 10 | Plan Integration | ✅ Complete |
| 10B | Conflict Validation | ✅ Complete |
| 10C | Test Stability Validation | ✅ Complete |
| 11 | Holistic Plan Sync | ✅ Complete |

📊 **Issues:** 78 | **Conflicts:** 0 | **Effort:** 48h

---

## ⛔ FORBIDDEN Behaviors

**❌ NEVER DO THESE:**
- Ask "Should I proceed?" or "Do you want me to continue?"
- Wait for user confirmation before starting next phase
- Output "Ready for next phase?" messages
- Pause execution after analysis
- Generate partial reports and stop
- Generate Markdown files after every action (Master Orchestrator blocks this)
- Display full progress table after every phase (use minimal 3-row update)
- Use ASCII box-drawing characters (┌ ─ ┐ │ └ ┘) - breaks on mobile

**✅ ALWAYS DO THESE:**
- Execute ALL 12 phases in sequence automatically
- Show full progress table ONLY at start and end
- Use minimal 3-row update during execution
- Generate final consolidated report at Phase 11 completion
- Proceed to next phase immediately after current phase completes

---

# 🔍 SEARCH PIPELINE (Phases 0-4)

## 📋 Canonical Source of Truth (CORTEX 6.0)

**Primary Sources:**
- **Requirements:** `cortex6/requirements/CX6-requirements.yaml` (820 lines)
  - 18 Strategic/Foundation/Cross-Repo requirements
  - 18 DoR decisions (Q1-Q20, 100% complete)
  - 16 Architectural decisions (AD-001 to AD-016)
  - Risk register, success metrics

- **Acceptance Criteria:** `cortex6/requirements/CX6-acceptance-criteria.yaml` (5,717 lines)
  - 361 acceptance criteria across 26 sections
  - 14 categories (governance, audit, orchestrators, dashboard, toolkit, etc.)
  - Test files, validation methods, evidence requirements

- **Master Plan:** `cortex6/artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml` (1,403 lines)
  - 5 stages: Foundation (40-48h) → Quality (24-32h) → Features (60-80h) → Hardening (40-60h) → Enhancements (40-60h)
  - Total effort: 210-288 hours (5.3-7.2 weeks)
  - DOR status: 100% (zero ambiguity)

- **Dashboard Plan:** `cortex6/artifacts/PLAN-VIEWER-DASHBOARD-PLAN.yaml` (1,233 lines)
  - 4 phases: Backend API (4-5h), Frontend SPA (6-8h), Integration (3-4h), Polish (3-4h)
  - 7 acceptance criteria (AC-DASH-001 to AC-DASH-007)
  - Tech stack: FastAPI + WebSocket + Tailwind CSS

## 📊 Analysis Categories

### Category 1: Strategic Requirements Gap Detection (18 Requirements)

**Source:** `CX6-requirements.yaml` Section 1

| SR-ID | Requirement | Stage | Priority | AC Count |
|-------|-------------|-------|----------|----------|
| SR-001 | Comprehensive Audit Logging | 1 | P0_CRITICAL | AC-AUDIT-001 to AC-AUDIT-006 |
| SR-002 | AC-ID Traceability Framework | 1 | P0_CRITICAL | AC-VAL-001 to AC-VAL-004 |
| SR-003 | SKULL → CORE Rules Migration | 1 | P0_CRITICAL | AC-GOV-001 to AC-GOV-011 |
| SR-004 | Manual Housekeeping Orchestrator | 1 | HIGH | AC-HOUSE-001 to AC-HOUSE-009 |
| SR-005 | Cross-Repo Architecture | 3 | HIGH | AC-CROSS-001 to AC-CROSS-005 |
| SR-006 | Migrate Orchestrator (On-Demand) | 3 | MEDIUM | AC-MIGRATE-001 to AC-MIGRATE-006 |
| SR-007 | Fast Startup via Lazy Loading | 3 | MEDIUM | Performance SLA <500ms |
| SR-008 | Interactive Plan Viewer Dashboard | 3 | HIGH | AC-DASH-001 to AC-DASH-007 |

**Gap Detection:**
- Check if plan phases map to all 18 SR requirements
- Verify each SR has corresponding AC coverage
- Validate implementation tasks exist for each SR

### Category 2: Acceptance Criteria Implementation Gaps (361 Criteria)

**Source:** `CX6-acceptance-criteria.yaml` (26 sections)

| Section | AC Range | Risk Level | Criteria Count |
|---------|----------|------------|----------------|
| Section 1-4 | Governance & Compliance | 🔴 CRITICAL | AC-GOV-001 to AC-GOV-011 (11) |
| Section 15 | Audit Logging Framework | 🔴 CRITICAL | AC-AUDIT-001 to AC-AUDIT-006 (6) |
| Section 5-14 | Orchestrators | 🟠 HIGH | AC-ORC-* (100+) |
| Section 24 | TDD-Master Orchestrator | 🔴 CRITICAL | AC-TDD-MASTER-001 to AC-TDD-MASTER-007 (7) |
| Section 26 | Plan Viewer Dashboard | 🟠 HIGH | AC-DASH-001 to AC-DASH-007 (7) |
| Section 23 | CORTEX Toolkit | 🟠 HIGH | AC-TOOLKIT-001 to AC-TOOLKIT-008 (8) |
| Section 25 | YAML/JSON Data Interchange | 🔴 CRITICAL | AC-DATA-001 to AC-DATA-005 (5) |

**Gap Detection Checks:**
1. **Missing Implementation:** AC exists, no code/test found
2. **Partial Implementation:** Code exists but incomplete per AC
3. **Test Coverage Gap:** AC has no test file with @pytest.mark.ac_id() marker
4. **Audit Evidence Gap:** AC has no audit log coverage (per AC-VAL-002)
5. **Dual Validation Gap:** AC lacks both test + audit evidence (per AC-VAL-003)

### Category 3: CORE Rules Violations (61 Rules)

**Source:** `cortex-brain/tier0/governance/core-rules.yaml` (post-Stage 1.2 migration)

| Rule | Detection Pattern | Severity | Stage |
|------|-------------------|----------|-------|
| CORE-019 | TDD_MASTER_REQUIRED - Code without TDD-Master execution | 🔴 BLOCKED | 1 |
| CORE-001 | HOLISTIC_DISCOVERY - File creation without workspace search | 🔴 BLOCKED | 1 |
| CORE-015 | GIT_ISOLATION - CORTEX commits to user repos | 🔴 BLOCKED | All |
| CORE-012 | PLANNING_ISOLATION - Plans implement code | 🔴 BLOCKED | All |
| CORE-030 | YAML_SAFE_LOADER - yaml.load() without SafeLoader | 🔴 CRITICAL | All |

**Note:** Pre-Stage 1.2, check legacy `brain-protection-rules.yaml` for SKULL rules.

### Category 4: DoR Decision Alignment (18 Decisions)

**Source:** `CX6-requirements.yaml` metadata.dor_decisions (Q1-Q20)

| Decision | Question | Impact on Plan |
|----------|----------|----------------|
| Q3 | Backward compatibility? | Clean SKULL deletion (no migration code) |
| Q4 | Housekeeping triggers? | Manual only (no auto-triggers in plan) |
| Q5 | Deployment model? | Clone + PATH (no global install tasks) |
| Q17 | Dashboard HTML regen? | Generate once (no regeneration tasks) |
| Q18 | Auto-launch browser? | Manual default (--dashboard-launch flag optional) |
| Q19 | Server daemon mode? | Foreground default (--daemon optional) |
| Q20 | Data refresh pattern? | WebSocket push (no polling implementation) |

**Gap Detection:** Verify plan tasks comply with all 18 DoR decisions (no conflicting implementations)

### Category 5: Architecture Anti-Patterns

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

### Phase 0: Canonical Sources Loading
**Duration:** <10 seconds

**Actions:**
1. Load `CX6-requirements.yaml` (820 lines, 18 requirements, 18 DoR decisions)
2. Load `CX6-acceptance-criteria.yaml` (5,717 lines, 361 criteria, 26 sections)
3. Load `CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml` (1,403 lines, 5 stages)
4. Parse all strategic requirements, acceptance criteria, DoR decisions
5. Build validation checklist by category and stage
6. Identify blocking vs non-blocking criteria

**Phase Completion Output:**
```
✅ Phase 0 - Canonical Sources Loading: Complete
   └─ Requirements Loaded: 18 SR | DoR Decisions: 18 | AD: 16
   └─ Criteria Loaded: 361 | Sections: 26 | Categories: 14
   └─ Plan Loaded: 5 stages, 210-288h effort
   └─ AC Version: 17.0.0 | Requirements Version: 1.1.0
   └─ Duration: 5s
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

**⚡ INTELLIGENT GAP DETECTION:**
1. **Load Progress Tracker** (`cortex6/execution/tracking/progress-tracker.json`)
2. **Extract Completed AC IDs** from tracker's `evidence.ac_validated` arrays
3. **Filter Out Completed Work** - Skip gaps for AC IDs marked COMPLETE
4. **Verify Implementation Exists** - Check for matching test/source files
5. **Report Only Real Gaps** - No false positives for already-complete work

**Discrepancy Types:**
- **MISSING** - AC criterion exists, no code found, NOT in progress tracker
- **PARTIAL** - Code exists but incomplete
- **STALE** - Code outdated vs spec
- **CONFLICT** - Code differs from AC
- **OVER** - Code exceeds AC scope

**🛡️ Protection:** Prevents reporting on work already validated in progress tracker.

**Phase Completion Output:**
```
✅ Phase 2 - Discrepancy Detection: Complete
   └─ Progress Tracker Loaded: {completed_count} AC IDs marked complete
   └─ Discrepancies Found: {count} (after filtering completed work)
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

**Per AC-VAL-002:** Verify every criterion has audit log coverage

**Primary Output:** `cortex6/analysis/search-findings-{timestamp}.yaml`

```yaml
search_findings:
  generated_at: '2026-01-09T19:00:00Z'
  requirements_version: '1.1.0'
  ac_version: '17.0.0'
  plan_version: '2.0.0'
  
  sources:
    requirements: 'cortex6/requirements/CX6-requirements.yaml'
    acceptance_criteria: 'cortex6/requirements/CX6-acceptance-criteria.yaml'
    master_plan: 'cortex6/artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml'
  
  summary:
    total_issues: 78
    critical: 24  # Blocking Stage 1 execution
    high: 31      # Should address in current stage
    medium: 18    # Address in next stage
    low: 5        # Enhancements stage
    
  strategic_requirements_gaps:
    - sr_id: SR-001
      name: "Comprehensive Audit Logging"
      stage: 1
      gap_type: PARTIAL_IMPLEMENTATION
      description: "AuditLogger exists but missing <5ms latency validation"
      evidence_found: ["src/infrastructure/audit_logger.py"]
      evidence_missing: ["tests/performance/test_audit_latency.py"]
      severity: CRITICAL
      blocking: true
      ac_coverage: ["AC-AUDIT-001", "AC-AUDIT-002"]
      
    - sr_id: SR-008
      name: "Interactive Plan Viewer Dashboard"
      stage: 3
      gap_type: NOT_STARTED
      description: "Dashboard plan exists but no implementation"
      evidence_found: ["cortex6/artifacts/PLAN-VIEWER-DASHBOARD-PLAN.yaml"]
      evidence_missing: ["src/dashboard/", "cortex6/dashboard/"]
      severity: HIGH
      blocking: false
      ac_coverage: ["AC-DASH-001" to "AC-DASH-007"]
      
  acceptance_criteria_gaps:
    - ac_id: AC-GOV-001
      section: "Governance & Compliance"
      type: PARTIAL
      description: "SKULL → CORE migration incomplete"
      evidence_found: ["cortex-brain/tier0/governance/"]
      evidence_missing: ["tests/governance/test_core_rules.py"]
      severity: CRITICAL
      blocking: true
      stage: 1
      phase: "1.2"
      
  dor_violations:
    - decision_id: Q17
      decision: "Dashboard HTML generated once (not regenerated)"
      violation_type: NOT_YET_IMPLEMENTED
      description: "Dashboard generator not yet built"
      severity: MEDIUM
      blocking: false
      stage: 3
      
  violations:
    - rule: CORE-030
      rule_name: "YAML_SAFE_LOADER"
      file: "src/utils/config_loader.py"
      line: 45
      pattern: "yaml.load(f)"
      fix: "yaml.safe_load(f)"
      severity: CRITICAL
      stage: 1
      
  brittleness:
    - type: RACE_CONDITION
      file: "src/database/state_manager.py"
      description: "Concurrent writes without locking"
      severity: CRITICAL
      ac_reference: "AC-CONC-001"
      stage: 1
      
  audit_gaps:
    - ac_id: AC-DASH-001
      section: "Plan Viewer Dashboard"
      gap_type: NO_AUDIT_COVERAGE
      description: "Dashboard server init has no audit logging"
      severity: HIGH
      stage: 3
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
   └─ Checking: {plan_path}/acceptance-criteria/CX6-requirements.yaml
   └─ Found existing → Moving to archive/remediation-plan-{date}.yaml
   └─ Archive complete ✅
```

**Lifecycle Rules:**
| Rule | Description |
|------|-------------|
| **ARCHIVE_BEFORE_REGENERATE** | Move existing `CX6-requirements.yaml` to `archive/` with timestamp |
| **SINGLE_ACTIVE_PLAN** | Only ONE `CX6-requirements.yaml` exists (no timestamps in active) |
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
   └─ Output: CX6-requirements.yaml
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
   └─ Auto-proceeding to Phase 10B...
```

---

### Phase 10B: Conflict Detection & Validation (NEW)
**Duration:** 1-2 minutes | **BLOCKING:** Yes

**⚠️ CRITICAL: This phase prevents regressions and conflicts before final sync**

**Validation Checks:**

| Check | Description | Action on Failure |
|-------|-------------|-------------------|
| **CONFLICT_DETECTION** | Scan new gaps vs existing tasks for contradictions | Flag conflicts, require resolution |
| **DUPLICATE_DETECTION** | Check if gap already exists with different ID | Merge duplicates, preserve earliest ID |
| **REGRESSION_ANALYSIS** | Verify injected Phase 0 doesn't invalidate completed work | Warn if regression risk detected |
| **TDD_ENFORCEMENT** | All remediation tasks must have test requirements | Block if no test_file specified |

**Conflict Detection Algorithm:**
```python
def detect_conflicts(new_gaps, existing_plan):
    """
    Detects conflicts between new remediation gaps and existing plan tasks.
    
    Conflict Types:
    1. CONTRADICTORY - New gap says "do X", existing task says "do opposite of X"
    2. DUPLICATE - Same criterion addressed by different IDs
    3. REGRESSION - Fixing gap would undo completed phase work
    4. DEPENDENCY_BREAK - Gap fix breaks dependency chain
    """
    conflicts = []
    
    for gap in new_gaps:
        # Check for contradictory requirements
        for task in existing_plan.all_tasks():
            if is_contradictory(gap.fix, task.implementation):
                conflicts.append({
                    "type": "CONTRADICTORY",
                    "gap_id": gap.id,
                    "task_id": task.id,
                    "resolution_required": True
                })
        
        # Check for duplicates
        if existing_plan.has_criterion(gap.criterion):
            conflicts.append({
                "type": "DUPLICATE",
                "gap_id": gap.id,
                "existing_id": existing_plan.get_criterion_id(gap.criterion),
                "action": "MERGE"
            })
        
        # Check for regression risk
        for completed_phase in existing_plan.completed_phases():
            if gap.affects(completed_phase):
                conflicts.append({
                    "type": "REGRESSION_RISK",
                    "gap_id": gap.id,
                    "affected_phase": completed_phase.name,
                    "severity": "WARNING"
                })
    
    return conflicts
```

**Phase Completion Output (Success):**
```
✅ Phase 10B - Conflict Validation: Complete
   └─ Conflicts Checked: {count} gaps × {count} existing tasks
   └─ Duplicates Merged: {count}
   └─ Regressions Detected: 0 ✅
   └─ TDD Compliance: 100% ✅
   └─ Duration: 60s
   └─ Auto-proceeding to Phase 11...
```

**Phase Output (Conflicts Found - BLOCKING):**
```
⚠️ Phase 10B - Conflict Validation: CONFLICTS DETECTED
   └─ Contradictory: {count} (BLOCKING - requires resolution)
   └─ Duplicates: {count} (auto-merged)
   └─ Regression Risk: {count} (WARNING - review recommended)
   └─ TDD Missing: {count} (BLOCKING - add test_file)
   └─ Action: Resolve conflicts before Phase 11
   └─ Output: conflict-report-{timestamp}.yaml
   └─ ⚠️ PHASE 11 BLOCKED until conflicts resolved
```

**Conflict Report Structure:**
```yaml
conflict_report:
  generated_at: '2026-01-09T12:00:00Z'
  total_conflicts: 5
  blocking_conflicts: 2
  
  conflicts:
    - type: CONTRADICTORY
      gap_id: AC-GAPFIX-NEW-001
      task_id: TASK-042
      gap_requirement: "Remove global state from StateManager"
      task_implementation: "Add global cache to StateManager for performance"
      resolution_options:
        - "Keep task, reject gap"
        - "Keep gap, mark task for revision"
        - "Merge: Add scoped cache instead of global"
      status: REQUIRES_RESOLUTION
      
    - type: DUPLICATE
      gap_id: AC-SEC-NEW-007
      existing_id: AC-SEC-003
      action: MERGED
      preserved_id: AC-SEC-003
      status: AUTO_RESOLVED
      
    - type: REGRESSION_RISK
      gap_id: AC-ARCH-NEW-012
      affected_phase: "Phase 2: Foundation Layer"
      affected_tasks: ["TASK-015", "TASK-016"]
      severity: WARNING
      recommendation: "Review before proceeding"
      status: ACKNOWLEDGED
```

---

### Phase 10C: Test Stability Validation
**Duration:** 2-4 minutes

**⚠️ CRITICAL: Ensures gap-fix changes don't destabilize existing tests**

**Purpose:**
Validate that all generated remediation code has corresponding test coverage and that existing tests remain stable after modifications.

**Actions:**
1. **Dependency Graph Analysis:** Build test dependency map for affected modules
2. **Test Impact Analysis:** Identify which tests may be affected by gap-fix changes
3. **Stability Validation:** Verify no circular dependencies or fragile test patterns introduced
4. **Coverage Gap Detection:** Ensure all new AC criteria have corresponding test requirements

**Validation Criteria:**
- [ ] All modified modules have corresponding test files
- [ ] No test-to-test dependencies that could cause cascade failures
- [ ] Test isolation verified (no shared mutable state)
- [ ] AC-to-test traceability maintained

**Phase Completion Output:**
```
📊 TEST STABILITY VALIDATION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modules Analyzed: {count}
Test Files Mapped: {count}
Dependency Depth: {max_depth}

Impact Analysis:
- Tests Affected: {count}
- New Tests Required: {count}
- Stability Risk: {LOW|MEDIUM|HIGH}

Coverage Mapping:
- AC Criteria: {total_ac}
- With Test Coverage: {covered}
- Coverage Gap: {gap_count} ({percentage}%)

Recommendations:
- {recommendation_1}
- {recommendation_2}
```

**Integration with Audit Logging:**
- Log test stability metrics to `audit_test_stability` table
- Enable MCP query: `mcp_audit_test_stability_report`
- Track stability trends over time for regression detection

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

**Date:** {date} | **Duration:** {total_duration} | **Status:** ✅ Complete

---

## Final Progress

| Overall | Progress | Status |
|---------|----------|--------|
| 🔍🔧 Gap-Fix | `██████████` 100% | ✅ Complete |

| Phase | Name | Status |
|-------|------|--------|
| 0 | AC Document Loading | ✅ |
| 1 | Implementation Scan | ✅ |
| 2 | Discrepancy Detection | ✅ |
| 3 | Violation Scan | ✅ |
| 4 | Audit Gap Analysis | ✅ |
| 5 | MCP Validation | ✅ |
| 6 | Load Findings | ✅ |
| 7 | Categorize | ✅ |
| 8 | Snowball Sort | ✅ |
| 9 | Plan Generation | ✅ |
| 10 | Plan Integration | ✅ |
| 10B | Conflict Validation | ✅ |
| 11 | Holistic Plan Sync | ✅ |

📊 **Issues:** {count} | **Conflicts:** {count} | **Effort:** {hours}h

---

## Summary

| Category | Total | Blocking |
|----------|-------|----------|
| Governance | {count} | {blocking} |
| Architecture | {count} | {blocking} |
| Security | {count} | {blocking} |
| **TOTAL** | **{total}** | **{blocking_total}** |

---

## 🌊 Snowball Order

| Phase | Focus | Unlocks |
|-------|-------|---------|
| 1 | Foundation | {count} criteria |
| 2 | Concurrency | Parallel testing |
| 3 | Security | Risk mitigation |

---

## 📁 Artifacts

- `search-findings-{timestamp}.yaml` (findings)
- `CX6-requirements.yaml` (active)
- `archive/remediation-plan-{date}.yaml` (previous)
- `conflict-report-{timestamp}.yaml` (if conflicts detected)
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

## 📁 File Locations (Canonical - CORTEX 6.0)

### Source of Truth Files

| Artifact | Location | Lines | Purpose |
|----------|----------|-------|---------|
| **Requirements** | `cortex6/requirements/CX6-requirements.yaml` | 820 | 18 SR, 18 DoR, 16 AD decisions |
| **Acceptance Criteria** | `cortex6/requirements/CX6-acceptance-criteria.yaml` | 5,717 | 361 AC across 26 sections |
| **Master Plan** | `cortex6/artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml` | 1,403 | 5-stage implementation plan |
| **Dashboard Plan** | `cortex6/artifacts/PLAN-VIEWER-DASHBOARD-PLAN.yaml` | 1,233 | Dashboard 4-phase plan |
| **Plan Config** | `cortex6/execution/config.yaml` | 164 | Execution configuration |
| **Navigation** | `cortex6/00-SOURCE-OF-TRUTH-README.md` | - | Canonical file guide |

### Gap-Fix Output Files

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Search Findings** | `cortex6/analysis/search-findings-{timestamp}.yaml` | Gap detection results |
| **Snowball Strategy** | `cortex6/analysis/snowball-strategy.yaml` | Prioritization order |
| **Conflict Report** | `cortex6/analysis/conflict-report-{timestamp}.yaml` | Phase 10B results |
| **Archive** | `cortex6/archive/` | Historical findings |

### Progress Tracking Files

| Artifact | Location | Purpose |
|----------|----------|---------|
| **Progress Tracker** | `cortex6/tracking/progress-tracker.json` | Machine-readable progress |
| **TODO List** | `cortex6/tracking/TODO.md` | Human-readable tasks |
| **Audit Logs** | `cortex-brain/audit-logs/*.jsonl` | Execution evidence |

### 🚫 FORBIDDEN File Creation Locations

**⚠️ SCOPE:** These restrictions apply **ONLY to CORTEX 6 planning files**. They do NOT restrict:
- Global CORTEX source code (`src/`, `tests/`, etc.)
- Brain infrastructure (`cortex-brain/tier*/`, `config/`, etc.)
- User repository operations
- Future CORTEX version planning

**SKULL RULE:** All CORTEX 6 acceptance/planning files MUST be created in canonical location ONLY.

**❌ NEVER create these CORTEX 6 files outside canonical location:**
- `CX6-acceptance-criteria.yaml` (or any `cortex-ac*.yaml` for CORTEX 6)
- `CX6-requirements.yaml` (or any `remediation-plan*.yaml` for CORTEX 6)
- `search-findings-*.yaml` (CORTEX 6 gap detection results)
- `snowball-strategy.yaml` (CORTEX 6 prioritization)
- Any CORTEX 6 acceptance criteria files

**✅ ONLY ALLOWED Location (CORTEX 6 Planning):**
```
cortex-brain/documents/planning/active/cortex6/requirements/
```

**🛡️ Enforcement:**
- Pre-execution validation checks file exists at canonical path
- Gap-fix orchestrator rejects operations on files in wrong location
- Archive old files to `acceptance-criteria/archive/` before regenerating

---

## ⚡ Invocation

**Standard (full 14-phase pipeline):**
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
| **CONFLICT_DETECTION** | ✅ Phase 10B validates no contradictions or regressions |
| **TDD_ENFORCEMENT** | ✅ Phase 10B enforces test_file on all remediation tasks |
| **MINIMAL_RESPONSE** | ✅ 3-row progress during execution, full table only at start/end |
| **NO_MD_GENERATION** | ✅ Master Orchestrator blocks MD file creation after actions |

---

## 📚 References

- **Main Entry Point:** `.github/prompts/CORTEX.prompt.md`
- **Canonical Requirements:** `cortex6/requirements/CX6-requirements.yaml` (820 lines)
- **Canonical AC:** `cortex6/requirements/CX6-acceptance-criteria.yaml` (5,717 lines)
- **Master Plan:** `cortex6/artifacts/CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml` (1,403 lines)
- **Dashboard Plan:** `cortex6/artifacts/PLAN-VIEWER-DASHBOARD-PLAN.yaml` (1,233 lines)
- **MCP Server:** `src/mcp/align_plan_sync.py` (Phase 11 implementation)
- **Orchestrators Docs:** `cortex-brain/documents/orchestrators-quick-ref.md`

---

**Version History:**
- v1.5.0 (2026-01-11): **Progress Tracker Integration** - Phase 2 now loads progress-tracker.json, filters out completed AC IDs, verifies implementation existence before reporting gaps (fixes false positives for completed work like SKULL tests)
- v1.4.0 (2026-01-09): **Aligned with CORTEX 6.0 Canonical Sources** - Updated to reference CX6-requirements.yaml (18 SR, 18 DoR, 16 AD), CX6-acceptance-criteria.yaml (361 AC, 26 sections), CORTEX6-COMPREHENSIVE-UPGRADE-PLAN.yaml (5 stages, 210-288h), phase outputs now include strategic requirements gaps, DoR decision violations, stage/phase mapping
- v1.3.0 (2026-01-09): Added Phase 10C - Test Stability Validation (AC-GAPFIX-005 to AC-GAPFIX-007)
- v1.2.0 (2026-01-09): Mobile-friendly progress display - removed ASCII borders, minimal 3-row updates during execution
- v1.1.0 (2026-01-09): Added Phase 10B - Conflict Detection & Validation (AC-GAPFIX-001 to AC-GAPFIX-004)
- v1.0.0 (2026-01-09): Initial release - combined search + align into unified 12-phase pipeline

