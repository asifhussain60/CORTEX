# 🔍🔧 CORTEX Gap-Fix - Holistic Gap Detection & Remediation

**Version:** 1.2.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Analysis + Remediation  
**Author:** Asif Hussain | **AC Reference:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-acceptance-criteria.yaml`  
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

## 📋 Analysis Categories

### Category 1: AC Implementation Gaps
**Source of Truth:** `CX6-acceptance-criteria.yaml`

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
1. Load `CX6-acceptance-criteria.yaml`
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
  ac_location: 'cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-acceptance-criteria.yaml'
  
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

## 📁 File Locations (Canonical)

| Artifact | Location |
|----------|----------|
| **AC Source of Truth** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-acceptance-criteria.yaml` |
| **Search Findings** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/search-findings-{timestamp}.yaml` |
| **Remediation Plan** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-requirements.yaml` |
| **Snowball Strategy** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/snowball-strategy.yaml` |
| **Archive** | `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/archive/` |

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
cortex-brain/documents/planning/active/cortex6/acceptance-criteria/
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
- **AC Source:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/CX6-acceptance-criteria.yaml`
- **MCP Server:** `src/mcp/align_plan_sync.py` (Phase 11 implementation)
- **Orchestrators Docs:** `cortex-brain/documents/orchestrators-quick-ref.md`

---

**Version History:**
- v1.3.0 (2026-01-09): Added Phase 10C - Test Stability Validation (AC-GAPFIX-005 to AC-GAPFIX-007)
- v1.2.0 (2026-01-09): Mobile-friendly progress display - removed ASCII borders, minimal 3-row updates during execution
- v1.1.0 (2026-01-09): Added Phase 10B - Conflict Detection & Validation (AC-GAPFIX-001 to AC-GAPFIX-004)
- v1.0.0 (2026-01-09): Initial release - combined search + align into unified 12-phase pipeline

