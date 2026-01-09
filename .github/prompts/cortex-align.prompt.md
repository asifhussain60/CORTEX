# 🔧 CORTEX Align - Plan Realignment with Visual Progress Tracking

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Remediation  
**Author:** Asif Hussain | **AC Reference:** `.asif/AI-Learning/cortex6/acceptance/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

**AUTONOMOUS PLAN REALIGNMENT** - Consumes findings from `cortex-search` and:
1. **Prioritizes fixes** using snowball effect ordering
2. **Generates remediation plan** with effort estimates
3. **Integrates into existing feature plans** (if applicable)
4. **Proposes AC enhancements** for uncovered patterns
5. **Shows incremental progress** via ASCII visual progress bars

**⚠️ CRITICAL: This is FULLY AUTONOMOUS - executes all phases without user confirmation.**

---

## 🔀 Intent Routing

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
- Execute ALL 6 phases in sequence automatically
- Show visual progress tracker at phase transitions
- Generate final consolidated report at Phase 6 completion
- Proceed to next phase immediately after current phase completes

---

## 🔬 Alignment Pipeline (6 Phases)

### 📊 Visual Progress Tracker Template

**Show this at EACH phase transition:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🔧 CORTEX ALIGN - PLAN REALIGNMENT                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overall Progress: `████████░░░░░░░░░░░░` 40% 🔄 IN PROGRESS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Phase 1 - Load Findings      `██████████` 100% ✅ Complete                  │
│ Phase 2 - Categorize         `██████████` 100% ✅ Complete                  │
│ Phase 3 - Snowball Sort      `████████░░`  80% 🔄 In Progress               │
│ Phase 4 - Plan Generation    `░░░░░░░░░░`   0% ⏳ Pending                   │
│ Phase 5 - Plan Integration   `░░░░░░░░░░`   0% ⏳ Pending                   │
│ Phase 6 - AC Enhancement     `░░░░░░░░░░`   0% ⏳ Pending                   │
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

**Actions:**
1. Generate phased remediation plan
2. Assign effort estimates per phase
3. Calculate total effort
4. Create YAML plan structure

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
   └─ Plan Phases: 7 | Total Effort: 40h | Blocking Fixed: 12
   └─ Output: cortex-brain/analysis/remediation-plan-{timestamp}.yaml
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
   └─ ALL PHASES COMPLETE

| Phase | Progress | Status |
|-------|----------|--------|
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `██████████` | 100% ✅ |
| Phase 5 - Plan Integration | `██████████` | 100% ✅ |
| Phase 6 - AC Enhancement | `██████████` | 100% ✅ |
```

---

## 📝 Final Report Template

**Generated ONLY after Phase 6 completion:**

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
| Phase 1 - Load Findings | `██████████` | 100% ✅ |
| Phase 2 - Categorize | `██████████` | 100% ✅ |
| Phase 3 - Snowball Sort | `██████████` | 100% ✅ |
| Phase 4 - Plan Generation | `██████████` | 100% ✅ |
| Phase 5 - Plan Integration | `██████████` | 100% ✅ |
| Phase 6 - AC Enhancement | `██████████` | 100% ✅ |

📊 **Issues Processed:** {count} | **Plan Phases:** {phases} | **Effort:** {hours}h

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

## 📈 AC Enhancement Proposals

1. **{AC-NEW-001}:** {description}
2. **{AC-NEW-002}:** {description}
3. **{AC-NEW-003}:** {description}

---

## 📁 Generated Artifacts

- `cortex-brain/analysis/remediation-plan-{timestamp}.yaml`
- `cortex-brain/analysis/ac-enhancements-{timestamp}.md`
- `{plan_path}/tracking/progress-tracker.json` (updated)

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

---

## 🛡️ Brain Protection Compliance

| SKULL Rule | Compliance |
|------------|------------|
| **PLANNING_ISOLATION** | ✅ Generates plans, does NOT implement fixes |
| **HOLISTIC_DISCOVERY** | ✅ Considers entire findings set |
| **GIT_ISOLATION** | ✅ Only modifies CORTEX planning files |

---

## 📚 References

- **Search Prompt:** `.github/prompts/cortex-search.prompt.md`
- **AC Source:** `.asif/AI-Learning/cortex6/acceptance/00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml`
- **Snowball Strategy:** `cortex-brain/documents/planning/active/*/tracking/snowball.md`

---

**Version History:**
- v1.0.0 (2026-01-09): Initial release - visual progress tracking with snowball prioritization
