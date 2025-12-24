# 🧠 CORTEX Unified Planning System - Gap Analysis
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

**Analysis Date:** December 16, 2025  
**Scope:** Unified Planning System Requirements vs Current Implementation  
**Status:** ⚠️ SIGNIFICANT GAPS IDENTIFIED

---

## 🎯 Executive Summary

**Finding:** Current CORTEX implementation has a **partial** planning system that handles some workflows but is **missing critical components** of the unified system described in user expectations.

**Gap Severity:** 🔴 HIGH - Core workflow differences require architectural changes

**Key Gaps:**
1. ❌ No automatic hidden plan folder creation for implicit requests
2. ❌ Missing dedicated conversational/clarification Markdown file
3. ⚠️ Incomplete CORTEX LENS integration for structural analysis
4. ⚠️ No explicit plan rejection → folder deletion workflow
5. ⚠️ Complexity-based plan decomposition exists but routing incomplete
6. ✅ Master plan template compliance (00-master-plan.md structure exists)

---

## 📋 Detailed Gap Analysis

### 1. Plan Initiation & Folder Structure

#### **Expected Behavior:**
> "Whenever a user submits a request—whether or not they use the word 'plan'—immediately enter planning mode by creating a hidden plan folder with a standardized subfolder structure and a dedicated Markdown file used exclusively for iterative clarification"

#### **Current Implementation:**
- **File:** `src/entry_point/planning_gate.py`
- **Status:** ⚠️ PARTIAL
- **What Exists:**
  - `PlanningGate` class with complexity classification (Tier 1-4)
  - Creates plan folders in `cortex-brain/documents/planning/features/temp-plans/`
  - Generates temporary plan ID: `TEMP-PLAN-{timestamp}-{request_slug}`
  - Creates placeholder `README.md` with user request

**Gaps:**
- ❌ **NOT automatic for all requests** - Only triggered when explicitly routed to planning
- ❌ **NOT hidden** - Plans created in visible `temp-plans/` directory
- ❌ **No standardized subfolder structure** - Only creates root folder + README
- ❌ **No dedicated conversational/clarification Markdown** - README is static placeholder

**Evidence:**
```python
# From planning_gate.py line 186-198
# Create plan folder
plan_folder = self.temp_plans_dir / temp_plan_id
plan_folder.mkdir(parents=True, exist_ok=True)

# Create placeholder README  <- NOT conversational/interactive
readme_path = plan_folder / "README.md"
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(f"""# Temporary Plan: {temp_plan_id}
**Created:** {datetime.now().isoformat()}
**Tier:** {tier}
**User Request:** {request}
**Status:** ⏳ Awaiting approval
```

**Required Changes:**
1. Hook `PlanningGate` into **ALL** user request entry points (not just explicit planning)
2. Create hidden subfolder structure: `context/`, `artifacts/`, `analysis/`
3. Generate interactive `clarification.md` file for back-and-forth refinement
4. Track conversation state in clarification file (Q&A history)

---

### 2. Clarification Mode & Conversational Workflow

#### **Expected Behavior:**
> "Remain in clarification mode until the user explicitly approves the plan. [...] a dedicated Markdown file used exclusively for iterative clarification and back-and-forth with the user"

#### **Current Implementation:**
- **File:** `src/operations/modules/orchestration/temporary_plan_manager.py`
- **Status:** ⚠️ PARTIAL
- **What Exists:**
  - `TemporaryPlanManager` class handles plan creation and updates
  - `update_temporary_plan()` method accepts user feedback
  - Tracks feedback in `user_feedback` list
  - Approval tracking (`approved` flag, `approval_timestamp`)

**Gaps:**
- ❌ **No explicit clarification mode state** - No FSM state for "CLARIFYING" vs "AWAITING_APPROVAL"
- ❌ **No conversational Markdown file** - Feedback stored in JSON, not interactive document
- ❌ **No workflow to "remain in clarification mode"** - Code doesn't enforce staying until approval
- ⚠️ Unclear how system knows when to stop asking questions vs present for approval

**Evidence:**
```python
# From temporary_plan_manager.py line 44-51
user_feedback: List[Dict[str, str]] = field(default_factory=list)  
# [{"timestamp": "...", "feedback": "..."}]
approved: bool = False
approval_timestamp: Optional[datetime] = None
```

**Required Changes:**
1. Add `CLARIFICATION` state to plan lifecycle FSM
2. Create `clarification.md` file with Q&A structure:
   ```markdown
   ## 🗣️ Clarification Session
   
   ### Round 1 (Dec 16, 10:45 AM)
   **CORTEX:** [Questions about requirements]
   **User:** [Answers/feedback]
   
   ### Round 2 (Dec 16, 10:52 AM)
   **CORTEX:** [Follow-up questions]
   **User:** [Refinement]
   ```
3. Explicit transition: `CLARIFICATION` → `AWAITING_APPROVAL` (when CORTEX has enough info)
4. User can exit clarification with "looks good" / "approve" / "start execution"

---

### 3. CORTEX LENS Integration

#### **Expected Behavior:**
> "Upon approval, invoke CORTEX LENS to analyze the surrounding codebase and artifacts strictly within the approved scope by inspecting adjacent layers (files, modules, dependencies, interfaces, tests, configurations, and workflows), generating structural representations including AST graphs, dependency maps, and contextual summaries, and saving all such artifacts immutably inside the plan folder."

#### **Current Implementation:**
- **Files:** Tests reference CORTEX LENS (`tests/test_cortex_lens_*.py`)
- **Status:** 🔴 INCOMPLETE INTEGRATION
- **What Exists:**
  - CORTEX LENS exists as separate system with documentation
  - Test files show it can generate analysis reports, AST graphs
  - References in completed plans (cortex-evolution-v3.9) mention "AST Enhancement v1.0"

**Gaps:**
- ❌ **No automatic invocation on plan approval** - No code path from approval → LENS
- ❌ **No scope-based analysis** - No mechanism to limit LENS to "approved scope"
- ❌ **No artifact saving to plan folder** - LENS output not written to plan context
- ❌ **Missing integration points:**
  - `PlanLifecycleManager.approve_plan()` doesn't call LENS
  - `TemporaryPlanManager._convert_to_master_plan()` doesn't invoke LENS
  - No LENS wrapper in planning orchestrator

**Evidence:**
```python
# From plan_lifecycle_manager.py line 262-290
def approve_plan(self, plan_id: str, approved_by: str = "user") -> ApprovalResult:
    """Approve plan for transition to ACTIVE."""
    # ... state transition logic ...
    # ❌ NO CORTEX LENS INVOCATION HERE
    return ApprovalResult(approved=True, ...)
```

**Required Changes:**
1. Create `CortexLensIntegration` class in planning orchestrator
2. On approval, invoke LENS analysis:
   ```python
   lens_results = self.lens.analyze_scope(
       scope_files=plan_scope_files,
       output_dir=plan_folder / "artifacts" / "lens-analysis"
   )
   ```
3. Generate and save:
   - AST graphs (`.json`, `.svg`)
   - Dependency maps (`.dot`, `.png`)
   - Contextual summaries (`.md`)
4. Update plan metadata with LENS artifacts paths

---

### 4. Complexity-Based Plan Decomposition

#### **Expected Behavior:**
> "Using the approved intent and the derived structural context, assign a complexity score that determines plan decomposition. If complexity is low, convert the planning Markdown into a single master plan; if complexity is high, convert it into a master plan plus structured sub-plans"

#### **Current Implementation:**
- **File:** `src/operations/modules/routing/planning_intelligence_coordinator.py`
- **Status:** ✅ IMPLEMENTED (but not fully integrated)
- **What Exists:**
  - `ComplexityAnalyzer` assigns complexity tiers (CRITICAL/HIGH/MEDIUM/LOW)
  - `PlanningIntelligenceCoordinator` combines complexity + test value scoring
  - Routing logic exists for different planning modes
  - Master plan template system in `unified_plan_generator.py`

**Gaps:**
- ⚠️ **Partial routing** - Complexity analysis done but not always enforced at entry point
- ⚠️ **Sub-plan generation inconsistent** - No clear rule: "HIGH complexity → auto-create sub-plans"
- ⚠️ **Missing explicit mapping:** Complexity → Master/Sub-plan structure

**Evidence:**
```python
# From planning_intelligence_coordinator.py line 100-120
class PlanningMode(Enum):
    INCREMENTAL_FULL_TDD = "incremental_full_tdd"
    INCREMENTAL_TARGETED_TDD = "incremental_targeted_tdd"
    INCREMENTAL_NO_TDD = "incremental_no_tdd"
    SKELETON_TARGETED_TDD = "skeleton_targeted_tdd"
    SKELETON_NO_TDD = "skeleton_no_tdd"
    DIRECT_EXECUTION = "direct_execution"
# ✅ Modes exist, but not consistently enforced
```

**Required Changes:**
1. Enforce complexity routing at `PlanningGate` level (before any work starts)
2. Add explicit decision logic:
   ```python
   if complexity >= ComplexityTier.HIGH:
       generate_master_plan()
       generate_sub_plans()  # One per phase
   else:
       generate_single_master_plan()
   ```
3. Update unified plan generator to auto-create sub-plan files

---

### 5. Master Plan Template Compliance

#### **Expected Behavior:**
> "The master plan must be created exactly following the attached master plan file, with the same executive sections, in the same order, with the same level of detail, formatting, metrics, progress tracking, and narrative structure"

#### **Current Implementation:**
- **File:** `cortex-brain/documents/planning/active/cortex-rearchitecture-v1/00-master-plan.md`
- **Status:** ✅ COMPLIANT TEMPLATE EXISTS
- **What Exists:**
  - Canonical master plan template with all required sections
  - `MasterPlanTemplate` class enforces section order
  - `UnifiedPlanGenerator` uses template system
  - Token optimization and visual progress tracking implemented

**Gaps:**
- ⚠️ **Not enforced everywhere** - Some plans may not use unified generator
- ⚠️ Template compliance validation only in tests, not runtime

**Evidence:**
```python
# From unified_plan_generator.py line 200-250
def generate_master_plan(
    self,
    plan_id: str,
    phases: List[Dict],
    metadata: Dict,
    # ... many options for customization
) -> str:
    """Generate master plan with consistent structure following 
    canonical section order."""
# ✅ Template system exists and works
```

**Required Changes:**
1. Make `UnifiedPlanGenerator` the ONLY path for master plan creation
2. Add runtime validation: Reject plans that don't match template schema
3. Create `validate_master_plan_structure()` utility

---

### 6. Plan Rejection & Cleanup

#### **Expected Behavior:**
> "If the user rejects the plan at any stage, immediately delete the entire plan folder and all generated artifacts and return to an idle, non-executing state"

#### **Current Implementation:**
- **File:** `src/planning/plan_lifecycle_manager.py`
- **Status:** ⚠️ PARTIAL
- **What Exists:**
  - State machine with transitions (can transition back to TEMP from AWAITING_APPROVAL)
  - Folder movement capabilities

**Gaps:**
- ❌ **No explicit rejection handler** - No `reject_plan()` method
- ❌ **No automatic folder deletion** - Rejection would leave plan in `temp-plans/`
- ❌ **No cleanup on rejection** - LENS artifacts, logs, etc. would remain
- ❌ **No "return to idle" mechanism** - System state unclear after rejection

**Evidence:**
```python
# From plan_lifecycle_manager.py line 115-120
# Register valid transitions
fsm.register_transition(PlanState.AWAITING_APPROVAL.value, PlanState.TEMP.value)  
# ✅ Transition exists
# ❌ But no handler that deletes folder
```

**Required Changes:**
1. Add `reject_plan(plan_id: str, reason: str)` method:
   ```python
   def reject_plan(self, plan_id: str, reason: str):
       plan_folder = self._get_plan_folder(plan_id)
       shutil.rmtree(plan_folder)  # Delete entire plan
       del self._state_machines[plan_id]  # Clean state
       logger.info(f"Plan {plan_id} rejected and deleted: {reason}")
   ```
2. Hook rejection command to lifecycle manager
3. Return CORTEX to idle state (clear current plan context)

---

### 7. Continuation Prompts in Sub-Plans

#### **Expected Behavior:**
> "Every sub-plan must contain [...] a continuation prompt suitable for resuming work in a new Copilot chat"

#### **Current Implementation:**
- **File:** `src/operations/modules/planning/unified_plan_generator.py`
- **Status:** ✅ IMPLEMENTED
- **What Exists:**
  - Continuation prompt generation in plan generator
  - Tests validate continuation prompt presence
  - Ultra-compact format with manifest references

**Gaps:**
- ⚠️ Only in master plans, unclear if ALL sub-plans get continuations
- ⚠️ Continuation prompt removed when plan 100% complete (by design, but user wants it always?)

**Evidence:**
```python
# From test_token_display_enhancements.py line 74-77
assert '## 🔄 Continuation Prompt' in plan  # ✅ Present

# line 90-91
assert '## 🔄 Continuation Prompt' not in plan  # When 100% complete
```

**Required Changes:**
1. Verify sub-plans also get continuation prompts
2. Clarify user requirement: Keep continuation even when 100% complete? Or only during execution?

---

### 8. Sub-Plan Master Plan Update Instructions

#### **Expected Behavior:**
> "Every sub-plan must contain explicit instructions to update the master plan upon completion, including phase status, decisions, risks, metrics, token impact, running totals, and progress indicators"

#### **Current Implementation:**
- **File:** Tests show update instructions exist
- **Status:** ⚠️ PARTIAL
- **What Exists:**
  - Tests validate update reminder present
  - Token tracking system exists

**Gaps:**
- ❌ **Not verified in actual sub-plan files** - Need to check real sub-plan structure
- ⚠️ Instructions may be generic, not specific to what fields to update

**Evidence:**
```python
# From test_unified_plan_generator.py line 387-390
"""GREEN: Should include reminder to update metrics in continuation prompt."""
# ✅ Test exists, but actual implementation unclear
```

**Required Changes:**
1. Add explicit section to ALL sub-plans:
   ```markdown
   ## 📝 Master Plan Update Instructions
   
   Upon completion of this sub-plan, update 00-master-plan.md:
   1. Phase X status: ⏳ → ✅ COMPLETE
   2. Add to "Decisions" section: [key decisions made]
   3. Update "Risk Analysis": [any new risks or mitigations]
   4. Update progress bar: [X/Y phases complete]
   5. Add token savings to running total
   6. Update "Actual Work Time" in metrics table
   ```

---

### 9. Repository Review Before Execution

#### **Expected Behavior:**
> "Before any execution, review existing repository functionality, constraints, and assumptions to identify gaps, risks, or missing prerequisites and reflect them explicitly in the plan"

#### **Current Implementation:**
- **Status:** ❌ NOT IMPLEMENTED
- **What Exists:**
  - Nothing - No pre-execution repository scan

**Gaps:**
- ❌ **No repository review step** in any orchestrator
- ❌ **No constraint identification** before plan execution
- ❌ **No prerequisite checking** (e.g., dependencies installed, tools available)

**Required Changes:**
1. Add pre-execution phase to `PlanningOrchestrator`:
   ```python
   def review_repository_context(self, plan: FeaturePlan):
       """Review repo before execution."""
       # Check existing code patterns
       # Identify constraints (tech stack, conventions)
       # Validate prerequisites
       # Update plan with findings
   ```
2. Save review results to `context/repository-review.md` in plan folder
3. Block execution if critical prerequisites missing

---

## 🔄 Implementation Roadmap

### Phase 1: Core Workflow Fixes (HIGH PRIORITY)
1. ✅ Automatic planning gate for ALL requests
2. ✅ Conversational clarification.md file
3. ✅ Plan rejection → folder deletion
4. ✅ Explicit clarification mode state

**Estimated Effort:** 16-24 hours

---

### Phase 2: CORTEX LENS Integration (HIGH PRIORITY)
1. ✅ LENS invocation on plan approval
2. ✅ Scope-based analysis
3. ✅ Artifact saving to plan folder
4. ✅ AST graph, dependency map generation

**Estimated Effort:** 24-32 hours

---

### Phase 3: Pre-Execution Repository Review (MEDIUM PRIORITY)
1. ✅ Repository scanning utility
2. ✅ Constraint identification
3. ✅ Prerequisite validation
4. ✅ Review report generation

**Estimated Effort:** 12-16 hours

---

### Phase 4: Sub-Plan Enhancement (MEDIUM PRIORITY)
1. ✅ Continuation prompts in all sub-plans
2. ✅ Explicit master plan update instructions
3. ✅ Standardized subfolder structure

**Estimated Effort:** 8-12 hours

---

### Phase 5: Enforcement & Validation (LOW PRIORITY)
1. ✅ Runtime template compliance validation
2. ✅ Complexity routing enforcement
3. ✅ End-to-end integration tests

**Estimated Effort:** 16-20 hours

---

## 🎯 Summary of Gaps

| Component | Status | Severity | Effort |
|-----------|--------|----------|--------|
| Automatic plan folder creation | ⚠️ PARTIAL | 🔴 HIGH | 8h |
| Conversational clarification file | ❌ MISSING | 🔴 HIGH | 12h |
| CORTEX LENS integration | 🔴 INCOMPLETE | 🔴 HIGH | 24h |
| Plan rejection cleanup | ⚠️ PARTIAL | 🟡 MEDIUM | 4h |
| Complexity-based decomposition | ✅ EXISTS | 🟢 LOW | 4h (routing) |
| Master plan template compliance | ✅ COMPLIANT | 🟢 LOW | 0h |
| Continuation prompts | ✅ IMPLEMENTED | 🟢 LOW | 2h (verify sub-plans) |
| Sub-plan update instructions | ⚠️ PARTIAL | 🟡 MEDIUM | 4h |
| Repository review | ❌ MISSING | 🟡 MEDIUM | 16h |

**Total Estimated Effort:** 74-84 hours

---

## 🔍 Recommended Next Steps

1. **Clarify User Intent:**
   - Is the hidden plan folder requirement a security/UX concern?
   - Should clarification mode be MANDATORY for all Tier 3+ work?
   - What triggers "enough clarification" → move to approval?

2. **Prioritize Fixes:**
   - **Phase 1** (Core Workflow) is blocking for user expectations
   - **Phase 2** (CORTEX LENS) provides the "structural context" promised

3. **Create New Plan:**
   - Use CORTEX planning system to implement fixes
   - Complexity Tier: 4 (COMPLEX - multi-phase architectural changes)
   - Estimated: 80h (10 days @ 1 sr engineer)

4. **Autonomous Execution:**
   - Once plan approved, execute all phases without re-confirmation
   - Use visual progress tracking (already implemented)

---

## 📚 References

- **Current Master Plan Template:** `cortex-brain/documents/planning/active/cortex-rearchitecture-v1/00-master-plan.md`
- **Planning Gate:** `src/entry_point/planning_gate.py`
- **Temporary Plan Manager:** `src/operations/modules/orchestration/temporary_plan_manager.py`
- **Planning Orchestrator:** `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`
- **Unified Plan Generator:** `src/operations/modules/planning/unified_plan_generator.py`
- **Plan Lifecycle Manager:** `src/planning/plan_lifecycle_manager.py`

---

**Analysis Complete:** December 16, 2025  
**Next Action:** User review → Approve fixes → Execute implementation plan
