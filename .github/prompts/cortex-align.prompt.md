# 🔧 CORTEX Align - Plan Realignment with Visual Progress Tracking

**Version:** 1.3.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Remediation  
**Author:** Asif Hussain | **AC Reference:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**AUTONOMOUS PLAN REALIGNMENT** - Consumes findings from `cortex-search` and:
1. **Archives previous remediation plans** (lifecycle management)
2. **Prioritizes fixes** using snowball effect ordering
3. **Generates fresh remediation plan** with effort estimates
4. **Integrates into existing feature plans** (if applicable)
5. **Proposes AC enhancements** for uncovered patterns
6. **Shows incremental progress** via ASCII visual progress bars

**⚠️ CRITICAL: This is FULLY AUTONOMOUS - executes all phases without user confirmation.**

---

## � Remediation Plan Lifecycle Management

**⚠️ CRITICAL STANDARD (AC-ALIGN-001):**

### File Organization
```
cortex-brain/documents/planning/active/{plan-name}/acceptance-criteria/
├── 00-{PLAN}-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml   # Source of truth
├── snowball-strategy.yaml                           # Prioritization framework
├── remediation-plan.yaml                            # ACTIVE remediation (singular)
└── archive/                                         # Previous remediations
    ├── remediation-plan-2026-01-08.yaml
    ├── remediation-plan-2026-01-07.yaml
    └── ...
```

### Lifecycle Rules
| Rule | Description |
|------|-------------|
| **ARCHIVE_BEFORE_REGENERATE** | Move existing `remediation-plan.yaml` to `archive/` with timestamp suffix before creating new |
| **SINGLE_ACTIVE_PLAN** | Only ONE `remediation-plan.yaml` exists (no timestamps in active filename) |
| **PLAN_SPECIFIC_LOCATION** | Remediation generated in plan's `acceptance-criteria/` folder, NOT in `cortex-brain/analysis/` |
| **TIMESTAMP_ON_ARCHIVE** | Archived files get `-{YYYY-MM-DD}` suffix |
| **PRESERVE_HISTORY** | Never delete archived remediations (audit trail) |

### Archive Protocol (Phase 4 Pre-Step)
```python
def archive_existing_remediation(plan_path):
    """
    Archive existing remediation before generating new one.
    
    Args:
        plan_path: e.g., cortex-brain/documents/planning/active/cortex6
    """
    ac_path = f"{plan_path}/acceptance-criteria"
    active_remediation = f"{ac_path}/remediation-plan.yaml"
    archive_dir = f"{ac_path}/archive"
    
    if file_exists(active_remediation):
        # Ensure archive directory exists
        create_directory(archive_dir)
        
        # Get timestamp from file or use current date
        timestamp = get_file_date(active_remediation) or today()
        archived_name = f"remediation-plan-{timestamp}.yaml"
        
        # Move to archive
        move_file(active_remediation, f"{archive_dir}/{archived_name}")
        
        log_audit("REMEDIATION_ARCHIVED", {
            "from": active_remediation,
            "to": f"{archive_dir}/{archived_name}"
        })
```

---

## �🔀 Intent Routing

**Patterns:**
- `^(align|realign|fix plan|remediate|generate fix plan).*$`
- `^(align implementation|ac alignment|snowball plan).*$`

**Priority:** 7 (Critical - Remediation phase)  
**Mode:** Autonomous  
**Confidence:** 1.0

---

## 🤖 Autonomous Execution Mode

| Setting | Value | Description |
|---------|-------|-------------|
| **Auto-Proceed** | ✅ ENABLED | Phases execute sequentially without user confirmation |
| **Auto-Prioritize** | ✅ ENABLED | Snowball ordering applied automatically |
| **Visual Progress** | ✅ ENABLED | ASCII progress bars shown at each phase |
| **Pause Points** | ❌ NONE | No user interaction required between phases |

---

## ⛔ FORBIDDEN Behaviors

**❌ NEVER DO THESE:**
- Ask "Should I proceed?" or "Do you want me to continue?"
- Wait for user confirmation before starting next phase
- Output "Ready for next phase?" messages
- Pause execution after analysis
- Generate partial reports and stop

**✅ ALWAYS DO THESE:**
- Execute ALL 7 phases in sequence automatically
- Show visual progress tracker at phase transitions
- Generate final consolidated report at Phase 7 completion
- Proceed to next phase immediately after current phase completes

---

## 🔬 Alignment Pipeline (8 Phases - including Phase 0)

### Phase 0: MCP Tool Validation (Pre-Requisite)
**Duration:** <5 seconds | **BLOCKING:** Yes

**⚠️ CRITICAL: This phase MUST pass before proceeding**

**Validation Checks:**
| Check | File/Location | Required |
|-------|---------------|----------|
| MCP Tool Implementation | `src/mcp/align_plan_sync.py` | ✅ REQUIRED |
| Capability Registration | `src/mcp/capability_registry.py` → `cortex_align_plan_sync` | ✅ REQUIRED |
| MCP Export | `src/mcp/__init__.py` → `AlignPlanSyncTool` | ✅ REQUIRED |

**Validation Command:**
```bash
python3 -c "from src.mcp.align_plan_sync import AlignPlanSyncTool, align_plan_sync; tool = AlignPlanSyncTool(); print(f'✅ MCP Tool: {tool.NAME}')"
```

**Phase 0 Output (Success):**
```
✅ Phase 0 - MCP Validation: Complete
   └─ Tool: cortex_align_plan_sync ✅ Found
   └─ Capability: Registered ✅
   └─ Auto-proceeding to Phase 1...
```

**Phase 0 Output (Failure - BLOCKING):**
```
❌ Phase 0 - MCP Validation: FAILED
   └─ Tool: cortex_align_plan_sync ❌ NOT FOUND
   └─ Required File: src/mcp/align_plan_sync.py
   └─ BLOCKING: Cannot proceed to Phase 7 without MCP tool
   └─ Action: Create MCP tool or check imports
   └─ ⚠️ ALIGN ABORTED - Fix MCP tool first
```

**If Phase 0 fails:** Generate remediation task and HALT execution.

---

### 📊 Visual Progress Tracker Template

**Show this at EACH phase transition:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🔧 CORTEX ALIGN - PLAN REALIGNMENT                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overall Progress: `████████░░░░░░░░░░░░` 40% 🔄 IN PROGRESS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Phase 0 - MCP Validation     `██████████` 100% ✅ Complete                  │
│ Phase 1 - Load Findings      `██████████` 100% ✅ Complete                  │
│ Phase 2 - Categorize         `██████████` 100% ✅ Complete                  │
│ Phase 3 - Snowball Sort      `████████░░`  80% 🔄 In Progress               │
│ Phase 4 - Plan Generation    `░░░░░░░░░░`   0% ⏳ Pending                   │
│ Phase 5 - Plan Integration   `░░░░░░░░░░`   0% ⏳ Pending                   │
│ Phase 6 - AC Enhancement     `░░░░░░░░░░`   0% ⏳ Pending                   │
│ Phase 7 - Holistic Plan Sync `░░░░░░░░░░`   0% ⏳ Pending                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Phase 1: Load Search Findings
**Duration:** <10 seconds

```
✅ Phase 1 - Load Findings: Starting
   └─ Loading: cortex-brain/analysis/search-findings-*.yaml
```

**Actions:**
1. Load latest `search-findings-{timestamp}.yaml`
2. Parse all discrepancies, violations, brittleness, audit gaps
3. Validate findings structure
4. Count issues by severity

**Phase Completion Output:**
```
✅ Phase 1 - Load Findings: Complete
   └─ Issues Loaded: 68 | Critical: 18 | High: 29 | Medium: 17 | Low: 4
   └─ Duration: 2s
   └─ Auto-proceeding to Phase 2...

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `░░░░░░░░░░` | 0% 🔄 Starting |
```

---

### Phase 2: Categorize & Analyze
**Duration:** 1-2 minutes

**Actions:**
1. Group issues by category (governance, architecture, security, etc.)
2. Identify blocking issues (must fix first)
3. Calculate downstream impact for each issue
4. Map issue dependencies

**Categories:**
| Category | Issues | Blocking |
|----------|--------|----------|
| Governance | {count} | {blocking_count} |
| Architecture | {count} | {blocking_count} |
| Security | {count} | {blocking_count} |
| Concurrency | {count} | {blocking_count} |
| Performance | {count} | {blocking_count} |
| Audit Gaps | {count} | {blocking_count} |

**Phase Completion Output:**
```
✅ Phase 2 - Categorize: Complete
   └─ Categories: 6 | Blocking Issues: 12 | Dependencies Mapped: 45
   └─ Duration: 45s
   └─ Auto-proceeding to Phase 3...

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `░░░░░░░░░░` | 0% 🔄 Starting |
```

---

### Phase 3: Snowball Prioritization
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
✅ Phase 3 - Snowball Sort: Complete
   └─ Priority Layers: 7 | Snowball Impact Calculated
   └─ Layer 1 (Blocking): 12 issues → Unlocks 45 downstream
   └─ Layer 2 (Foundation): 8 issues → Unlocks 23 downstream
   └─ Duration: 30s
   └─ Auto-proceeding to Phase 4...

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `░░░░░░░░░░` | 0% 🔄 Starting |
```

---

### Phase 4: Generate Remediation Plan
**Duration:** 2-3 minutes

**Pre-Step: Archive Existing Remediation**
```
🔄 Phase 4.0 - Archive Existing: Starting
   └─ Checking: {plan_path}/acceptance-criteria/remediation-plan.yaml
   └─ Found existing → Moving to archive/remediation-plan-{date}.yaml
   └─ Archive complete ✅
```

**Actions:**
1. **Archive existing remediation** (if exists) to `archive/` folder
2. Generate phased remediation plan
3. Assign effort estimates per phase
4. Calculate total effort
5. Create YAML plan structure at `{plan_path}/acceptance-criteria/remediation-plan.yaml`

**Plan Structure:**
```yaml
remediation_plan:
  generated_at: '2026-01-09T10:30:00Z'
  total_issues: 68
  blocking_issues: 12
  estimated_effort: "40 hours"
  
  phases:
    - phase: 1
      name: "Foundation Blockers"
      priority: "🔴 CRITICAL"
      issues:
        - id: AC-GOV-001
          description: "SKULL rule migration incomplete"
          effort: "2h"
          fix: "Migrate remaining 15 rules to CORE-* numbering"
        - id: AC-F01-004
          description: "StateManager WAL mode not enabled"
          effort: "1h"
          fix: "Enable WAL mode in SQLite connection"
      estimated_hours: 8
      snowball_impact: "Unlocks 15 downstream criteria"
      
    - phase: 2
      name: "Concurrency Safety"
      priority: "🔴 CRITICAL"
      issues:
        - id: AC-RACE-001
          description: "StateManager race conditions"
          effort: "3h"
          fix: "Add optimistic locking with version columns"
      estimated_hours: 6
      snowball_impact: "Enables parallel orchestrator testing"
```

**Phase Completion Output:**
```
✅ Phase 4 - Plan Generation: Complete
   └─ Archived: remediation-plan-2026-01-08.yaml
   └─ Plan Phases: 7 | Total Effort: 40h | Blocking Fixed: 12
   └─ Output: {plan_path}/acceptance-criteria/remediation-plan.yaml
   └─ Duration: 90s
   └─ Auto-proceeding to Phase 5...

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `██████████` | 100% ✅ |
| Phase 5 - Plan Integration | `░░░░░░░░░░` | 0% 🔄 Starting |
```

---

### Phase 5: Integrate with Feature Plan
**Duration:** 1-2 minutes

**Actions:**
1. Check for associated plan in `cortex-brain/documents/planning/active/`
2. If exists: Inject findings as new phase (position 0 for blockers)
3. Reorder existing phases for snowball effect
4. Update progress tracker JSON
5. Generate continuation prompt

**Integration Logic:**
```python
def integrate_with_plan(remediation_plan, plan_path):
    plan = load_plan(plan_path)
    
    # Insert blocking issues as Phase 0
    if remediation_plan.has_blocking():
        plan.insert_phase(
            position=0,
            name="Critical Blockers (Align)",
            tasks=remediation_plan.blocking_issues,
            snowball_impact="Unlocks all downstream work"
        )
    
    # Add non-blocking to appropriate phases
    for issue in remediation_plan.non_blocking:
        matching_phase = plan.find_matching_phase(issue)
        if matching_phase:
            matching_phase.add_task(issue)
        else:
            plan.backlog.add(issue)
    
    plan.reorder_for_snowball_effect()
    plan.save()
```

**Phase Completion Output:**
```
✅ Phase 5 - Plan Integration: Complete
   └─ Plan Found: cortex6-build
   └─ New Phase Added: "Critical Blockers (Align)" at position 0
   └─ Tasks Added: 12 blocking + 15 high priority
   └─ Duration: 45s
   └─ Auto-proceeding to Phase 6...

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `██████████` | 100% ✅ |
| Phase 5 - Plan Integration | `██████████` | 100% ✅ |
| Phase 6 - AC Enhancement | `░░░░░░░░░░` | 0% 🔄 Starting |
```

---

### Phase 6: AC Enhancement Recommendations
**Duration:** 1-2 minutes

**Actions:**
1. Identify implementation patterns not covered by AC
2. Generate AC enhancement proposals
3. Estimate impact of each enhancement
4. Output recommendations file

**Enhancement Discovery:**
- Missing test coverage criteria
- Missing performance SLAs
- Missing security checks
- Edge cases not in AC

**Phase Completion Output:**
```
✅ Phase 6 - AC Enhancement: Complete
   └─ Enhancements Proposed: 5
   └─ Output: cortex-brain/analysis/ac-enhancements-{timestamp}.md
   └─ Duration: 30s
   └─ Auto-proceeding to Phase 7...

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `██████████` | 100% ✅ |
| Phase 5 - Plan Integration | `██████████` | 100% ✅ |
| Phase 6 - AC Enhancement | `██████████` | 100% ✅ |
| Phase 7 - Holistic Plan Sync | `░░░░░░░░░░` | 0% 🔄 Starting |
```

---

### Phase 7: Holistic Plan Synchronization (MCP)
**Duration:** 2-5 minutes

**⚠️ CRITICAL: This phase invokes Python via MCP for holistic alignment**

**Pre-Requisite:** Phases 1-6 must be complete

**Actions:**
1. **Invoke MCP Tool:** `cortex_align_plan_sync` via MCP server
2. **Holistic Review:** AC YAML + Remediation Plan + Snowball Strategy
3. **Plan Decision:**
   - **No Plan Exists:** Create new plan following Planning Orchestrator structure
   - **Plan Exists:** Revise and realign incorporating gaps, enhancements, user requests
4. **Snowball Optimization:** Reorder for maximum momentum building
5. **Alignment Validation:** Ensure AC, requirements.yaml, plan are perfectly aligned

**MCP Invocation:**
```python
# Invoke via MCP (NEVER direct execution)
mcp_request = {
    "method": "cortex_align_plan_sync",
    "params": {
        "ac_file": "{plan_path}/acceptance-criteria/00-*-ACCEPTANCE-CRITERIA.yaml",
        "remediation_file": "{plan_path}/acceptance-criteria/remediation-plan.yaml",
        "snowball_file": "{plan_path}/acceptance-criteria/snowball-strategy.yaml",
        "plan_path": "{plan_path}",
        "mode": "auto"  # "create" | "revise" | "auto"
    }
}
```

**Plan Sync Logic:**
```python
def align_plan_sync(ac_file, remediation_file, snowball_file, plan_path, mode="auto"):
    """
    Holistic plan synchronization - creates or revises plan for snowball alignment.
    
    1. Load all source files (AC, remediation, snowball)
    2. Detect if plan exists
    3. If no plan: Create using Planning Orchestrator structure
    4. If plan exists: Revise incorporating gaps and enhancements
    5. Ensure perfect alignment between AC ↔ requirements.yaml ↔ plan
    6. Optimize for snowball effect (blocking → foundation → security → ...)
    """
    
    # Step 1: Load sources
    ac = load_yaml(ac_file)
    remediation = load_yaml(remediation_file)
    snowball = load_yaml(snowball_file)
    
    # Step 2: Check plan existence
    plan_exists = check_plan_structure(plan_path)
    
    if mode == "auto":
        mode = "revise" if plan_exists else "create"
    
    # Step 3: Execute appropriate action
    if mode == "create":
        return create_new_plan(ac, remediation, snowball, plan_path)
    else:
        return revise_existing_plan(ac, remediation, snowball, plan_path)


def create_new_plan(ac, remediation, snowball, plan_path):
    """
    Create new plan following Planning Orchestrator v5 structure.
    
    Structure determined by scope:
    - Epic (>50 criteria, multi-phase): Full epic structure with features/
    - Feature (<50 criteria, focused): Simple feature structure
    """
    
    criteria_count = count_pending_criteria(ac)
    
    if criteria_count > 50:
        structure = "epic"
        # Create: context/, artifacts/, reports/, tracking/, features/
    else:
        structure = "feature"
        # Create: context/, artifacts/, reports/, tracking/
    
    # Generate requirements.yaml from AC + remediation
    requirements = generate_requirements_from_ac(ac, remediation)
    
    # Apply snowball ordering
    requirements = apply_snowball_ordering(requirements, snowball)
    
    # Create plan files
    create_plan_structure(plan_path, structure, requirements)
    
    return {"action": "created", "structure": structure, "criteria": criteria_count}


def revise_existing_plan(ac, remediation, snowball, plan_path):
    """
    Revise existing plan incorporating gaps, enhancements, user requests.
    
    Steps:
    1. Load existing plan state
    2. Identify gaps (AC criteria not in plan)
    3. Identify enhancements (new remediation tasks)
    4. Merge into plan phases
    5. Reorder for snowball effect
    6. Update requirements.yaml
    7. Regenerate progress-tracker.json
    """
    
    # Load existing
    existing_plan = load_plan(plan_path)
    existing_requirements = load_yaml(f"{plan_path}/context/requirements.yaml")
    
    # Find gaps
    gaps = find_ac_gaps(ac, existing_plan)
    enhancements = find_remediation_enhancements(remediation, existing_plan)
    
    # Merge
    merged_plan = merge_into_plan(existing_plan, gaps, enhancements)
    
    # Snowball reorder
    merged_plan = apply_snowball_ordering(merged_plan, snowball)
    
    # Update requirements.yaml
    updated_requirements = sync_requirements_with_plan(existing_requirements, merged_plan, ac)
    save_yaml(f"{plan_path}/context/requirements.yaml", updated_requirements)
    
    # Regenerate tracker
    regenerate_progress_tracker(plan_path, merged_plan)
    
    return {
        "action": "revised",
        "gaps_added": len(gaps),
        "enhancements_added": len(enhancements),
        "total_tasks": count_tasks(merged_plan)
    }
```

**Phase Completion Output:**
```
✅ Phase 7 - Holistic Plan Sync: Complete
   └─ Mode: {create|revise}
   └─ Plan Structure: {epic|feature}
   └─ Gaps Added: {count}
   └─ Enhancements: {count}
   └─ Snowball Optimized: ✅
   └─ AC ↔ Requirements ↔ Plan: ALIGNED
   └─ Duration: 120s
   └─ ALL PHASES COMPLETE

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 0 - MCP Validation | `██████████` | 100% ✅ |
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `██████████` | 100% ✅ |
| Phase 5 - Plan Integration | `██████████` | 100% ✅ |
| Phase 6 - AC Enhancement | `██████████` | 100% ✅ |
| Phase 7 - Holistic Plan Sync | `██████████` | 100% ✅ |
```

---

## 📝 Final Report Template

**Generated ONLY after Phase 7 completion:**

```markdown
# 🔧 CORTEX Align Report

**Date:** {date}
**Duration:** {total_duration}
**Status:** ✅ ALL PHASES COMPLETE

---

## Visual Progress Tracker

### 🔧 PLAN REALIGNMENT COMPLETE

**Overall Progress:** `████████████████████` **100%** ✅ COMPLETE

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 0 - MCP Validation | `██████████` | 100% ✅ |
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `██████████` | 100% ✅ |
| Phase 5 - Plan Integration | `██████████` | 100% ✅ |
| Phase 6 - AC Enhancement | `██████████` | 100% ✅ |
| Phase 7 - Holistic Plan Sync | `██████████` | 100% ✅ |

📊 **Issues Processed:** {count} | **Plan Phases:** {phases} | **Effort:** {hours}h

---

## Executive Summary

| Category | Total | Blocking | Effort |
|----------|-------|----------|--------|
| Governance | {count} | {blocking} | {hours}h |
| Architecture | {count} | {blocking} | {hours}h |
| Security | {count} | {blocking} | {hours}h |
| Concurrency | {count} | {blocking} | {hours}h |
| Plan Viewer Dashboard | {count} | {blocking} | {hours}h |
| Audit Gaps | {count} | {blocking} | {hours}h |
| **TOTAL** | **{total}** | **{blocking_total}** | **{total_hours}h** |

---

## 🌊 Snowball Execution Order

**Phase 1:** Foundation Blockers ({hours}h) → Unlocks {count} criteria
**Phase 2:** Concurrency Safety ({hours}h) → Enables parallel testing
**Phase 3:** Audit Gaps ({hours}h) → Enables automated validation
**Phase 4:** Security ({hours}h) → Risk mitigation
**Phase 5:** Plan Viewer Dashboard ({hours}h) → Visual progress tracking
**Phase 6:** Performance ({hours}h) → SLA compliance
**Phase 7:** Quality ({hours}h) → Maintainability

---

## 🔄 Holistic Plan Sync Results

| Metric | Value |
|--------|-------|
| **Mode** | {create \| revise} |
| **Plan Structure** | {epic \| feature} |
| **Gaps Added** | {count} |
| **Enhancements Added** | {count} |
| **Total Tasks** | {count} |
| **Snowball Optimized** | ✅ |
| **Alignment Status** | AC ↔ Requirements ↔ Plan: ALIGNED |

---

## 📈 AC Enhancement Proposals

1. **{AC-NEW-001}:** {description}
2. **{AC-NEW-002}:** {description}
3. **{AC-NEW-003}:** {description}

---

## 📁 Generated Artifacts

- `{plan_path}/acceptance-criteria/remediation-plan.yaml` (active)
- `{plan_path}/acceptance-criteria/archive/remediation-plan-{date}.yaml` (previous)
- `cortex-brain/analysis/ac-enhancements-{timestamp}.md`
- `{plan_path}/tracking/progress-tracker.json` (updated)
- `{plan_path}/context/requirements.yaml` (synced with AC)

---

## 🚀 Next Steps

Run the remediation plan:
```
/CORTEX execute remediation-plan
```

Or continue existing plan:
```
/CORTEX continue {plan_name}
```

---

**Report Generated:** {timestamp}
**Report Location:** `cortex-brain/analysis/align-report-{date}.md`
```

---

## ⚡ Invocation

**Standard (requires search findings):**
```
/CORTEX align
```

**With specific plan integration:**
```
/CORTEX align --plan cortex6-build
```

**Full workflow (search + align):**
```
/CORTEX search and align
```

**Phase 7 only (plan sync):**
```
/CORTEX align --phase 7
```

---

## 🛡️ Brain Protection Compliance

| SKULL Rule | Compliance |
|------------|------------|
| **PLANNING_ISOLATION** | ✅ Generates plans, does NOT implement fixes |
| **HOLISTIC_DISCOVERY** | ✅ Considers entire findings set |
| **GIT_ISOLATION** | ✅ Only modifies CORTEX planning files |
| **ARCHIVE_BEFORE_REGENERATE** | ✅ Preserves remediation history |
| **MCP_ONLY_TOOL_ACCESS** | ✅ Phase 7 uses MCP for Python execution |

---

## 📚 References

- **Search Prompt:** `.github/prompts/cortex-search.prompt.md`
- **AC Source:** `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`
- **Snowball Strategy:** `cortex-brain/documents/planning/active/*/acceptance-criteria/snowball-strategy.yaml`
- **AC Standard:** `AC-ALIGN-001` (Remediation Plan Lifecycle Management)
- **MCP Server:** `src/mcp/align_plan_sync.py` (Phase 7 implementation)

---

**Version History:**
- v1.3.0 (2026-01-09): Added Phase 0 - MCP Tool Validation (blocking pre-requisite check)
- v1.2.0 (2026-01-09): Added Phase 7 - Holistic Plan Synchronization via MCP Python script
- v1.1.0 (2026-01-09): Added remediation lifecycle management (archive before regenerate)
- v1.0.0 (2026-01-09): Initial release - visual progress tracking with snowball prioritization
