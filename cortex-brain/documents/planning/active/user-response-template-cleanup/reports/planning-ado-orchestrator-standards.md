# 🎭 Planning & ADO Orchestrator Standards Report

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** 2025-12-30  
**Purpose:** Document how Planning and ADO orchestrators create plans and enforce standards

---

## 🎯 Executive Summary

This report documents the standards and requirements from Planning System 4.0.1 and ADO Planning 3.0.0 orchestrators, explaining how they create plans and what requirements they enforce. This analysis was used to add Phase 7 to the User Response Template Cleanup plan.

---

## 📋 Planning System 4.0.1 Standards

**Source:** `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`  
**Version:** 4.0.1 | **Status:** ACTIVE

### 1. Plan Structure Requirements

**Mandatory Folder Structure:**
```
cortex-brain/documents/planning/active/{PLAN_NAME}/
├── 00-master-plan.md    # Main plan with progress tracker
├── context/             # Context artifacts
├── reports/             # Progress reports
├── artifacts/           # Supporting files
└── tracking/            # progress-tracker.json
```

**Automation Tool:** `cortex-toolkit/core/utilities/plan_scaffold_generator.py`

**Enforcement:** Required for all new plans (see cortex-maintenance.prompt.md Phase 1)

### 2. Visual Progress Tracker Requirements

**Location:** Master plan (00-master-plan.md) and user responses

**Rendering Method:** `PlanningSession.render_progress_table()`

**Display Timing (CRITICAL):**

| Moment | What to Display | Lines in Manifest |
|--------|-----------------|-------------------|
| **Beginning** | Complete phase table with all phases | 130-132 |
| **After each phase** | Overall progress bar + next phase only | 133-135 |
| **Overall completion** | Complete phase table with all phases | 136-137 |

**Required Components:**
- Overall progress bar in table header row
- Phase number and name
- Status icons (✅ Complete, ⏳ Pending, ⏸️ Paused)
- Progress percentage per phase
- Duration per phase (human-readable)
- Token usage per phase
- Task completion ratio (X/Y format)
- TDD status (RED/GREEN/REFACTOR) when applicable

**Example Format:**
```markdown
**Overall Progress:** `████████████░░░░░░░░` **60%** 🔄 Phase 4 Complete

| Phase | Progress | Status | Duration | Tokens | Tasks |
|-------|----------|--------|----------|--------|-------|
| Phase 1 - Discovery | `██████████` | 100% ✅ | 2.5 hrs | 1200 | 5/5 |
| Phase 2 - Delete | `██████████` | 100% ✅ | 30 min | 800 | 3/3 |
| Phase 3 - Consolidate | `██████████` | 100% ✅ | 1.2 hrs | 1500 | 6/6 |
| Phase 4 - Create | `██████████` | 100% ✅ | 45 min | 900 | 3/3 |
| Phase 5 - Update Routing | `░░░░░░░░░░` | 0% ⏳ | - | - | 0/4 |
```

### 3. Phase Lifecycle Management

**Source:** Lines 356-373 in manifest

**Four Lifecycle Hooks:**

#### A. `on_phase_start`
```yaml
- validate_prerequisites  # Check required files exist
- create_checkpoint      # Git snapshot for rollback
- update_progress_tracker # Mark phase as "in-progress"
```

#### B. `on_phase_complete`
```yaml
- run_validation_gate         # Execute tests, checks
- if_pass: commit_work        # Git commit with standard message
- if_pass: update_master_plan # Update progress tracker
- if_pass: create_checkpoint  # Post-phase snapshot
- if_pass: transition_to_next_phase # Move forward
```

#### C. `on_validation_fail`
```yaml
- attempt_self_heal (max 3 retries) # Try automatic fixes
- rollback_to_checkpoint            # Revert changes
- log_failure_reason                # Record error details
- escalate_to_user                  # Ask for help
```

#### D. `on_critical_error`
```yaml
- emergency_rollback        # Immediate revert
- save_error_state          # Preserve debugging info
- notify_user_immediately   # Alert user
```

**Self-Healing Strategies:**
1. **Retry with backoff** (transient errors, network issues) - 3 attempts, exponential backoff
2. **Alternative approach** (test failures, validation errors) - 2 attempts
3. **Rollback and retry** (breaking changes, integration failures) - 1 attempt

### 4. Final Refactor Phase Enforcement

**Source:** Lines 628-668 in manifest

**⚠️ MANDATORY for all implementation plans**

**Purpose:** Ensure production-ready code quality after all features implemented

**Distinction from TDD Refactor:**

| TDD Refactor | Final Refactor |
|--------------|----------------|
| Micro-level cleanup | Macro-level whole-file review |
| Per-feature refactoring | Entire codebase review |
| Part of RED-GREEN-REFACTOR cycle | Separate final phase |
| Happens during development | Happens after all features complete |

**7 Validation Criteria:**
1. ✅ No broken HTML tags or structural issues
2. ✅ Zero duplicate or redundant code blocks
3. ✅ All function complexity ≤30 (cyclomatic complexity)
4. ✅ SOLID principles enforced
5. ✅ No dead code or unused imports
6. ✅ All tests passing (100% pass rate)
7. ✅ File is production-ready and maintainable

**Implementation Method:** `_enforce_final_refactor_phase()`

**Location:** `src/orchestrators/planning/planning_orchestrator.py`

### 5. Token Optimization (95% Reduction)

**Source:** Lines 52-58 in manifest

**Token Allocation:**
- Status-only view: 400 tokens (quick overview)
- Master hub: 1200 tokens (plan navigation)
- Phase-specific: 2500 tokens (detailed work)

**Total Reduction:** 95% from previous versions

**Pattern Version:** 1.0 (hierarchical structure)

### 6. Tiered Routing System

**4-Tier Classification:**

| Tier | Name | Threshold | Planning Type | Plan Required |
|------|------|-----------|---------------|---------------|
| 1 | INSTANT | < 2 seconds | Direct function call | ❌ No |
| 2 | LIGHTWEIGHT | < 10 seconds | Inline validation plan | ✅ Inline |
| 3 | DOCUMENTED | 10-60 minutes | Feature plan (single MD) | ✅ Markdown |
| 4 | COMPLEX | > 1 hour | Nested plan (master + sub-plans) | ✅ Nested |

**Complexity Dimensions:**
1. Code impact (lines changed, files affected)
2. Risk level (dependencies, breaking changes)
3. Domain complexity (business logic, algorithms)
4. Integration scope (external systems, APIs)

### 7. Pre-Planning Discovery

**Source:** Lines 95-116 in manifest

**Purpose:** Check for existing/recent plans before creating new ones

**Search Folders:**
- `active/` - Current work in progress (all time)
- `temp-plans/` - Unapproved/pending work (last 30 days)
- `completed/` - Recently archived plans (last 180 days)

**Overhead:** 30-60 seconds

**Recommendation Types:**
- `active_plan_exists` - Continue existing or create new version
- `temp_plan_exists` - Approve existing or create new
- `completed_plan_exists` - Reuse context from completed plan

---

## 🔷 ADO Planning Orchestrator 3.0.0 Standards

**Source:** `cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`  
**Version:** 3.0.0 | **Status:** ACTIVE  
**Inheritance:** `inherits_from: "planning-system-manifest.yaml"`

### 1. Inherited Standards from Planning System

**All Planning System standards apply, PLUS ADO-specific additions:**

✅ Acceptance Criteria Approval Gate (REQ-001)  
✅ Interactive DoR Workflow (REQ-002)  
✅ Contextual Review Integration (REQ-003)  
✅ SWAG Estimation via Swagger (REQ-004)  
✅ Visual Progress Rendering (REQ-005)  
✅ Learning Library Auto-Documentation (REQ-006)  
✅ Interactive Threat Modeling (REQ-007)  
✅ TDD Reminders Visibility (REQ-008)

### 2. ADO-Specific Progress Tracker Components

**Source:** Lines 74-84 in manifest

**Additional Metrics Beyond Planning System:**
- Work items created/planned count
- Story points total
- Phase-specific ADO item tracking

**Display Timing (Same as Planning System):**
- **Beginning:** Complete phase table + **work item summary**
- **Phase completion:** Overall progress + next phase
- **Completion:** Complete phase table + **work item summary**

**Template Reference:** `ado_execution_progress`

**Example Addition to Progress Table:**
```markdown
**Overall Progress:** `████████████░░░░░░░░` **60%**  
**ADO Items:** 12 created | **Story Points:** 34 | **Epics:** 2

| Phase | Progress | Status | ADO Items | Story Points |
|-------|----------|--------|-----------|--------------|
| Phase 1 - Planning | 100% ✅ | Complete | 3 Features | 8 SP |
| Phase 2 - Implementation | 50% ⏳ | In Progress | 5 Tasks | 13 SP |
```

### 3. Work Item Type Mapping

**Source:** Lines 144-155 in manifest

**Requirement:** REQ-ADO-002 (Critical priority)

| Plan Element | ADO Work Item Type |
|--------------|-------------------|
| Feature | Epic |
| Phase | Feature |
| Task | Task or User Story |
| Threat | Risk |

**Implementation Method:** `ADOPlanningOrchestrator.map_to_ado_types()`

### 4. Contextual Review Integration

**Source:** Lines 34-46 in manifest

**Requirement:** REQ-003 (Critical priority, IMPLEMENTED)

**Integration Flow:**
1. Review orchestrator called before ADO item creation
2. Findings categorized:
   - **Blocking issues** → ADO Impediments (highest priority)
   - **Critical issues** → Linked tasks in story (must-fix)
   - **Improvements** → Optional tasks (lower priority)

**Enhancement Date:** 2025-12-09

### 5. Story Point Estimation

**Source:** Lines 157-162 in manifest

**Requirement:** REQ-ADO-004 (High priority, PARTIAL)

**Conversion:** Effort hours → Fibonacci scale story points

**Implementation Method:** `ADOPlanningOrchestrator.convert_to_story_points()`

**Fibonacci Scale:** 1, 2, 3, 5, 8, 13, 21

### 6. Parent-Child Relationship Management

**Source:** Lines 164-169 in manifest

**Requirement:** REQ-ADO-003 (High priority, IMPLEMENTED)

**Hierarchy:** Epic > Feature > Task

**Validation:** ADO work items must be linked correctly in hierarchy

### 7. Additional ADO Requirements

**Partial/Missing Implementation:**

| Requirement | Priority | Status | Method |
|-------------|----------|--------|--------|
| Area Path & Iteration Assignment | Medium | ❌ Missing | `assign_area_and_iteration()` |
| Bulk Work Item Creation | High | ❌ Missing | `create_items_batch()` |
| Work Item Link Generation | Medium | ⏳ Partial | Template validation |

---

## 🔀 Comparison: Planning vs. ADO Orchestrators

### Similarities

1. **Progress Tracker:** Both use visual progress with phase tables
2. **Display Timing:** Both follow Beginning → Phase Completion → Overall Completion pattern
3. **Phase Lifecycle:** Both use same 4 hooks (start, complete, fail, critical)
4. **4-Folder Structure:** Both require context/, reports/, artifacts/, tracking/
5. **Token Optimization:** Both aim for concise, hierarchical plans

### Differences

| Aspect | Planning System | ADO Planning |
|--------|----------------|--------------|
| **Additional Metrics** | Token usage, test pass rate | Work items count, story points |
| **Work Item Mapping** | N/A | Feature→Epic, Phase→Feature, Task→Task |
| **External Integration** | Self-contained | Azure DevOps API integration |
| **Estimation** | Time-based | Story points (Fibonacci) |
| **Hierarchy Management** | Plan phases | ADO parent-child relationships |
| **Template Reference** | `autonomous_execution_progress` | `ado_execution_progress` |

### When to Use Which

**Use Planning System when:**
- Internal CORTEX development
- Code refactoring/cleanup
- Documentation projects
- System maintenance

**Use ADO Planning when:**
- Creating ADO work items
- Sprint planning
- Feature backlog management
- Team collaboration in Azure DevOps

---

## 🎯 How Orchestrators Create Plans

### Planning System Plan Creation Flow

```
1. Parse user request
2. Detect planning pattern (e.g., "/CORTEX Plan feature-x")
3. Run pre-planning discovery (30-60s)
   ├─ Search active/ for existing plans
   ├─ Search temp-plans/ for pending work
   └─ Search completed/ for context reuse
4. Classify tier (1-4) using complexity analyzer
5. IF tier >= 2:
   ├─ Create plan folder structure (4 subfolders)
   ├─ Generate 00-master-plan.md with progress tracker
   ├─ Create tracking/progress-tracker.json
   └─ STOP (do not implement)
6. Return plan location to user
```

### ADO Planning Plan Creation Flow

```
1. Parse user request
2. Detect ADO pattern (e.g., "ado story for feature-x")
3. Inherit Planning System flow (steps 1-5 above)
4. ADDITIONAL ADO STEPS:
   ├─ Run contextual review orchestrator
   ├─ Categorize findings (blocking, critical, improvements)
   ├─ Map plan elements to ADO types (Feature→Epic, etc.)
   ├─ Convert effort estimates to story points
   ├─ Create ADO work items in hierarchy
   ├─ Link work items to review findings
   └─ Add ADO metrics to progress tracker
5. Return plan + ADO work item links
```

### Key Difference

**Planning System:** Creates plan, STOPS (no implementation)  
**ADO Planning:** Creates plan + creates ADO work items (with links)

---

## 📚 Enforcement Mechanisms

### 1. CORTEX.prompt.md Intent Router

**Lines 23-50:** Planning detection MUST happen FIRST before any work

**Planning Patterns:**
- `/CORTEX Plan [feature]`
- `create a plan for [feature]`
- `make a plan for [feature]`

**Implementation Patterns:**
- `implement [feature]`
- `build [feature]`
- `create [feature]` (without "plan")

**Rule:** Planning pattern → CREATE STRUCTURE → STOP → DO NOT IMPLEMENT

### 2. Maintenance Prompt Enforcement

**Location:** `cortex-maintenance.prompt.md` (Phase 1)

**Rule:** All new plans MUST use `plan_scaffold_generator.py` for folder structure

**Benefits:**
- Consistent structure across all plans
- Reduces orchestrator overhead by ~30 seconds per plan
- Prevents missing folders or incorrect naming

### 3. Brain Protection Rules (SKULL)

**Rule:** TDD_ENFORCEMENT - Tests must fail before implementation  
**Application:** Final Refactor Phase must include test validation

**Rule:** HOLISTIC_DISCOVERY - Search before create  
**Application:** Pre-planning discovery (30-60s overhead)

**Rule:** GIT_ISOLATION - CORTEX code never commits to user repos  
**Application:** Phase lifecycle git automation

---

## 📊 Metrics & Performance Targets

### Planning System Targets

| Tier | Execution Time | Applies To |
|------|----------------|------------|
| Tier 1 (INSTANT) | < 2 seconds | Direct operations |
| Tier 2 (LIGHTWEIGHT) | < 10 seconds | Inline validation |
| Tier 3 (DOCUMENTED) | < 60 minutes | Feature plans |
| Tier 4 (COMPLEX) | Variable | Nested plans |

**Discovery Overhead:** < 60 seconds

### ADO Planning Targets

**Same as Planning System, PLUS:**
- ADO API authentication: < 2 seconds
- Work item creation: < 5 seconds per item
- Bulk creation: < 30 seconds for batch of 20 items

---

## ✅ Compliance Checklist for Plans

Use this checklist to validate any plan against orchestrator standards:

### Planning System 4.0.1 Compliance

- [ ] 4-folder structure (context/, reports/, artifacts/, tracking/)
- [ ] 00-master-plan.md exists
- [ ] Visual progress tracker present in master plan
- [ ] Progress tracker shows at beginning and completion
- [ ] Progress tracker shows "overall + next phase" during execution
- [ ] All phases have lifecycle documentation (start, complete, fail, critical)
- [ ] Final refactor phase included (if implementation plan)
- [ ] Token usage optimized (< 2500 tokens per phase)
- [ ] Pre-planning discovery documented (if applicable)
- [ ] Tier classification documented

### ADO Planning 3.0.0 Compliance

**All Planning System checks above, PLUS:**

- [ ] ADO metrics in progress tracker (work items, story points)
- [ ] Work item type mapping documented (Feature→Epic, etc.)
- [ ] Contextual review findings categorized
- [ ] Story point estimates provided (Fibonacci scale)
- [ ] Parent-child relationships defined
- [ ] ADO work item links included in response
- [ ] Area path and iteration specified (if applicable)

---

## 🔗 References

**Planning System Manifest:**  
`cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`

**ADO Planning Manifest:**  
`cortex-brain/manifests/orchestrators/ado-planning-manifest.yaml`

**CORTEX Entry Point:**  
`.github/prompts/CORTEX.prompt.md`

**Maintenance Enforcement:**  
`.github/prompts/cortex-maintenance.prompt.md`

**Plan Scaffold Generator:**  
`cortex-toolkit/core/utilities/plan_scaffold_generator.py`

**Planning Orchestrator Source:**  
`src/operations/modules/orchestration/planning_orchestrator.py`

---

**Last Updated:** 2025-12-30  
**Reviewed By:** Asif Hussain  
**Next Review:** 2025-01-15 (or when manifests updated)
