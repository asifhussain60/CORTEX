# 🎯 Planning System - Gap Remediation Master Plan

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Date:** December 17, 2025  
**Status:** 🔄 ACTIVE - Gap Analysis Complete  
**Priority:** HIGH - Critical Integration Gaps Identified

---

## ⚡ Executive Summary

**Gap Analysis Result:** Planning System infrastructure is **85% complete** but has **CRITICAL integration gaps** that prevent full operational capability.

**Current State:**
- ✅ All core components exist (TemporaryPlanManager, SessionContextManager, PlanLifecycleManager, etc.)
- ✅ SKULL enforcement rules defined (SKULL-011, SKULL-012, SKULL-013)
- ✅ Planning Orchestrator 4.0 initialized with Planning System components
- ❌ **CRITICAL:** Components NOT integrated into end-to-end workflow
- ❌ **CRITICAL:** Orchestrator methods exist but don't call underlying managers
- ❌ **MISSING:** Iterative refinement loop implementation in orchestrator
- ❌ **MISSING:** Plan generation and template rendering integration

**Impact:** Planning System appears complete but **CANNOT EXECUTE** real planning workflows.

**Remediation Scope:** 3 phases, ~8-12 hours  
**Risk Level:** MEDIUM (infrastructure exists, wiring needed)

---

## 📊 Gap Analysis - DoD Compliance Review

### ✅ COMPLETE (Infrastructure Layer)

| Component | Status | Evidence |
|-----------|--------|----------|
| **TemporaryPlanManager** | ✅ | `src/operations/modules/orchestration/temporary_plan_manager.py` (733 LOC) |
| **SessionContextManager** | ✅ | `src/operations/modules/orchestration/session_context_manager.py` (288 LOC) |
| **PlanLifecycleManager** | ✅ | `src/planning/plan_lifecycle_manager.py` (561 LOC) |
| **ComplexityAnalyzer** | ✅ | `src/orchestration_3_0/orchestrators/planning/complexity_analyzer.py` |
| **PlanManifestTracker** | ✅ | `src/orchestration_3_0/orchestrators/planning/plan_manifest_tracker.py` |
| **UnifiedPlanGenerator** | ✅ | `src/operations/modules/planning/unified_plan_generator.py` (1304 LOC) |
| **TaskInjector** | ✅ | `src/operations/modules/planning/task_injector.py` |
| **AuditLogger** | ✅ | `src/operations/modules/orchestration/audit_logger.py` |
| **SKULL Rules** | ✅ | SKULL-011, SKULL-012, SKULL-013 in `cortex-brain/brain-protection-rules.yaml` |
| **Templates** | ✅ | `cortex-brain/templates/planning/MASTER-PLAN-TEMPLATE.md`, SUB-PLAN-TEMPLATE.md |
| **Documentation** | ✅ | `cortex-brain/PLANNING-SYSTEM-3.0-GUIDE.md` (604 lines) |

### ❌ MISSING (Integration Layer)

| Gap | Severity | Impact |
|-----|----------|--------|
| **Orchestrator-Manager Integration** | 🔴 CRITICAL | Orchestrator methods don't call TemporaryPlanManager/SessionContextManager |
| **Iterative Refinement Loop** | 🔴 CRITICAL | `start_refinement_session()` exists but no back-and-forth implementation |
| **Plan Generation Integration** | 🔴 CRITICAL | UnifiedPlanGenerator not called from orchestrator |
| **Template Rendering** | 🔴 CRITICAL | Master/Worker plan templates not rendered |
| **DoR Validation Gate** | 🟡 HIGH | DoR validation exists but not blocking progression |
| **Plan Promotion** | 🟡 HIGH | Temp→Active promotion not fully wired |
| **Manifest Tracking** | 🟡 HIGH | Plan registration not integrated |
| **Auto-Task Injection** | 🟡 HIGH | TaskInjector not called during plan generation |
| **AST/Lens Context** | 🟡 HIGH | Context accumulation across iterations missing |
| **Audit Trail Integration** | 🟢 MEDIUM | AuditLogger exists but not called from all touchpoints |

### 🔍 Detailed Gap Breakdown

#### Gap #1: Orchestrator Method Stubs (CRITICAL)
**Location:** `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`

**Problem:**
```python
# Lines 906-965: Methods exist but are implementation stubs
def start_refinement_session(...) -> InteractiveRefinementSession:
    logger.info(f"🎭 Planning System: Starting refinement session")
    # Calls ComplexityAnalyzer ✅
    # Calls TemporaryPlanManager ✅
    # BUT: No iterative loop implementation ❌
    # BUT: No plan generation call ❌
    # BUT: No template rendering ❌

def handle_user_feedback(...) -> InteractiveRefinementSession:
    logger.info(f"🎭 Planning System: Processing user feedback")
    # Calls SessionContextManager for context loading ✅
    # Calls TemporaryPlanManager.refine_plan() ✅
    # BUT: No DoR validation ❌
    # BUT: No AST/Lens analysis ❌
    # BUT: No plan regeneration ❌
```

**Expected Behavior:**
```python
def start_refinement_session(...):
    # 1. Complexity analysis ✅
    complexity = self.complexity_analyzer.analyze(...)
    
    # 2. Create temp plan ✅
    session = self.temporary_plan_manager.start_refinement_session(...)
    
    # 3. ❌ MISSING: Generate initial plan MD
    initial_plan = self.unified_plan_generator.generate_temp_plan(...)
    
    # 4. ❌ MISSING: Run AST/Lens analysis
    ast_context = self.ast_engine.analyze(...)
    lens_context = self.cortex_lens.analyze(...)
    
    # 5. ❌ MISSING: Store context in temp plan folder
    self._store_context(session.temp_plan_path, ast_context, lens_context)
    
    # 6. ❌ MISSING: Calculate DoR score
    dor_score = self._calculate_dor(session, ast_context, lens_context)
    
    # 7. Return session with updated DoR
    return session
```

#### Gap #2: No Iterative Refinement Loop (CRITICAL)
**Expected Workflow:**
```
User: "Add authentication"
  ↓
Orchestrator.start_refinement_session()
  ├─ Create temp plan ✅
  ├─ Generate plan MD ❌ MISSING
  └─ Ask user for approval/feedback ❌ MISSING
      ↓
User: "Use OAuth for Google"
  ↓
Orchestrator.handle_user_feedback()
  ├─ Load session context ✅
  ├─ Update plan MD ❌ MISSING
  ├─ Re-run AST/Lens ❌ MISSING
  ├─ Recalculate DoR ❌ MISSING
  └─ Ask again ❌ MISSING
      ↓
      ↻ REPEAT UNTIL DoR 🟢 + USER APPROVES
```

**Current Implementation:**
- ✅ Single iteration supported
- ❌ No loop structure for back-and-forth
- ❌ No DoR threshold checking
- ❌ No approval detection

#### Gap #3: Plan Generation Not Integrated (CRITICAL)
**Problem:**
```python
# UnifiedPlanGenerator exists but is NEVER CALLED
# src/operations/modules/planning/unified_plan_generator.py

class UnifiedPlanGenerator:
    def generate_master_plan(...):  # ← NEVER CALLED
        """Generate master plan from template"""
        pass
    
    def generate_worker_plan(...):  # ← NEVER CALLED
        """Generate worker plan for phase"""
        pass
```

**Expected Integration:**
```python
# After DoR satisfied and user approves:
def approve_plan(session_id):
    # 1. Promote to active ✅ (PlanLifecycleManager)
    promotion = self.lifecycle_manager.promote_to_active(session_id)
    
    # 2. ❌ MISSING: Determine plan format
    is_single_phase = self.complexity_analyzer.is_single_phase(...)
    
    # 3. ❌ MISSING: Generate plans
    if is_single_phase:
        self.unified_plan_generator.generate_master_plan(...)
    else:
        self.unified_plan_generator.generate_master_plan(...)
        for phase in phases:
            self.unified_plan_generator.generate_worker_plan(...)
    
    # 4. ❌ MISSING: Inject standard tasks
    self.task_injector.inject_tasks(...)
    
    # 5. ❌ MISSING: Register in manifest
    self.manifest_tracker.register_plan(...)
    
    return promotion
```

#### Gap #4: DoR Validation Not Blocking (HIGH)
**Problem:**
```python
# DoR validation exists but doesn't block progression
def can_proceed_to_execution(dor_status, user_approval):
    # ❌ NOT IMPLEMENTED in orchestrator
    pass
```

**Expected Behavior:**
```python
def request_approval(session_id):
    session = self.get_session(session_id)
    
    # ❌ MISSING: Check DoR threshold
    if session.dor_score < 90:
        raise DoRNotSatisfiedError(
            f"DoR score {session.dor_score}% below 90% threshold"
        )
    
    # ✅ Proceed to approval
    return self.lifecycle_manager.request_approval(session_id)
```

#### Gap #5: AST/Lens Context Accumulation (HIGH)
**Expected Workflow:**
```python
# Each refinement iteration should:
def refine_plan(session_id, feedback):
    # 1. Load existing context
    session = self.get_session(session_id)
    prev_ast = self.load_ast_context(session)
    prev_lens = self.load_lens_context(session)
    
    # 2. ❌ MISSING: Re-analyze with new feedback
    new_ast = self.ast_engine.analyze(feedback, prev_ast)
    new_lens = self.cortex_lens.analyze(feedback, prev_lens)
    
    # 3. ❌ MISSING: Accumulate context
    merged_ast = self.merge_context(prev_ast, new_ast)
    merged_lens = self.merge_context(prev_lens, new_lens)
    
    # 4. ❌ MISSING: Store updated context
    self.store_context(session, merged_ast, merged_lens)
    
    # 5. ❌ MISSING: Recalculate DoR
    session.dor_score = self.calculate_dor(session, merged_ast, merged_lens)
    
    return session
```

---

## 🎯 Master Plan - Gap Remediation

### Phase 1: Orchestrator Integration (HIGH Priority)
**Goal:** Wire PlanningOrchestrator methods to underlying managers  
**Estimated Effort:** 3-4 hours

#### Tasks:
1. **Integrate TemporaryPlanManager**
   - [ ] Wire `start_refinement_session()` to create temp plan AND generate MD
   - [ ] Wire `refine_plan()` to update plan MD on each iteration
   - [ ] Wire `approve_plan()` to trigger promotion

2. **Integrate UnifiedPlanGenerator**
   - [ ] Call `generate_temp_plan()` during initial session creation
   - [ ] Call `update_temp_plan()` during each refinement iteration
   - [ ] Call `generate_master_plan()` after promotion to active
   - [ ] Call `generate_worker_plan()` for each phase (if multi-phase)

3. **Integrate DoR Validation**
   - [ ] Implement `_calculate_dor()` method in orchestrator
   - [ ] Add DoR threshold check in `request_approval()`
   - [ ] Block progression if DoR < 90%
   - [ ] Return clear error message with gaps

**Acceptance Criteria:**
- ✅ `start_refinement_session()` creates temp plan MD file
- ✅ `refine_plan()` updates plan MD with new content
- ✅ `approve_plan()` generates master/worker plans in active/
- ✅ DoR < 90% blocks approval with clear message

---

### Phase 2: Iterative Refinement Loop (HIGH Priority)
**Goal:** Implement back-and-forth workflow until DoR satisfied  
**Estimated Effort:** 3-4 hours

#### Tasks:
1. **AST/Lens Integration**
   - [ ] Add AST engine initialization in orchestrator `__init__`
   - [ ] Add Cortex Lens initialization
   - [ ] Implement `_run_ast_analysis()` method
   - [ ] Implement `_run_lens_analysis()` method
   - [ ] Store analysis results in `temp-plans/{folder}/context/`

2. **Context Accumulation**
   - [ ] Implement context merging logic across iterations
   - [ ] Load previous context before each refinement
   - [ ] Update context with new analysis
   - [ ] Track context growth over iterations

3. **DoR Calculation Logic**
   - [ ] Implement DoR scoring algorithm (0-100%)
   - [ ] Factor in: context completeness, ambiguity, file coverage
   - [ ] Return DoR status: 🔴 NOT READY / 🟡 NEEDS REFINEMENT / 🟢 READY
   - [ ] Include gap analysis in response

**Acceptance Criteria:**
- ✅ Each refinement iteration runs AST/Lens analysis
- ✅ Context accumulates across iterations (no data loss)
- ✅ DoR score recalculated after each iteration
- ✅ User sees DoR status + gaps after each response

---

### Phase 3: Plan Generation & Lifecycle (MEDIUM Priority)
**Goal:** Complete plan promotion and manifest tracking  
**Estimated Effort:** 2-4 hours

#### Tasks:
1. **Plan Promotion Workflow**
   - [ ] Call `PlanLifecycleManager.promote_to_active()` after approval
   - [ ] Verify atomic move from temp-plans/ to active/
   - [ ] Preserve context/ subfolder during move
   - [ ] Handle promotion failures with rollback

2. **Template Rendering**
   - [ ] Load MASTER-PLAN-TEMPLATE.md
   - [ ] Inject metadata (plan_id, dates, complexity)
   - [ ] Render master plan to active/{feature}/master-plan.md
   - [ ] For multi-phase: render WP##-Phase-Name.md for each phase

3. **Standard Task Injection**
   - [ ] Call `TaskInjector.inject_tasks()` for each worker plan
   - [ ] Add: Git checkpoints, TDD, docs, master plan updates
   - [ ] Verify tasks appear in rendered plan MD

4. **Manifest Tracking**
   - [ ] Call `PlanManifestTracker.register_plan()` after promotion
   - [ ] Write to `cortex-brain/documents/planning/active-plans-manifest.yaml`
   - [ ] Include metadata: plan_id, feature, dates, complexity, status

**Acceptance Criteria:**
- ✅ Approved plan atomically moves to active/
- ✅ Master plan rendered from template with correct metadata
- ✅ Worker plans rendered for each phase (if multi-phase)
- ✅ Standard tasks auto-injected in all plans
- ✅ Plan registered in active-plans-manifest.yaml

---

## 🧪 Testing Strategy

### Unit Tests (per Phase)
- **Phase 1:** Test orchestrator method integration
  - `test_start_refinement_creates_temp_plan_md`
  - `test_refine_plan_updates_plan_md`
  - `test_dor_validation_blocks_approval`
  
- **Phase 2:** Test iterative refinement
  - `test_ast_lens_analysis_runs_per_iteration`
  - `test_context_accumulates_across_iterations`
  - `test_dor_recalculation_after_feedback`
  
- **Phase 3:** Test plan generation
  - `test_plan_promotion_to_active`
  - `test_template_rendering_master_plan`
  - `test_task_injection_in_worker_plans`
  - `test_manifest_registration`

### Integration Tests (End-to-End)
- `test_full_planning_workflow_single_phase`
- `test_full_planning_workflow_multi_phase`
- `test_iterative_refinement_until_dor_satisfied`
- `test_approval_and_promotion_workflow`

### Manual Validation
- [ ] Start planning session: "Add authentication"
- [ ] Verify temp plan MD created
- [ ] Refine: "Use OAuth for Google"
- [ ] Verify plan MD updated + AST/Lens graphs in context/
- [ ] Verify DoR score displayed
- [ ] Approve plan
- [ ] Verify master/worker plans in active/
- [ ] Verify manifest entry created

---

## 📊 Progress Tracking

### Overall Completion: 0/3 Phases

```
Phase 1: Orchestrator Integration    [          ] 0/3 tasks
Phase 2: Iterative Refinement Loop   [          ] 0/3 tasks  
Phase 3: Plan Generation & Lifecycle [          ] 0/4 tasks
```

**Target Completion:** December 18-19, 2025  
**Next Milestone:** Phase 1 completion (Orchestrator Integration)

---

## 🔍 Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| **AST/Lens Integration Complexity** | 🟡 MEDIUM | Use existing AST engine, add lightweight wrapper |
| **DoR Scoring Algorithm** | 🟡 MEDIUM | Start with heuristic (file coverage + context completeness) |
| **Template Rendering Edge Cases** | 🟢 LOW | Templates already tested in UnifiedPlanGenerator |
| **Manifest YAML Corruption** | 🟢 LOW | Use atomic writes with backup |

---

## 🎯 Success Criteria (All DoD Items Met)

Planning System is considered **FULLY OPERATIONAL** when:

✅ **Core Functionality:**
- [ ] User request creates temp plan folder with MD file
- [ ] Iterative refinement loop works (back-and-forth)
- [ ] AST/Lens graphs generated per iteration
- [ ] DoR validation blocks approval if <90%
- [ ] Approved plan promotes to active/ atomically
- [ ] Master/worker plans rendered from templates
- [ ] Standard tasks auto-injected
- [ ] Plan registered in manifest

✅ **Testing:**
- [ ] All unit tests passing (100% pass rate)
- [ ] All integration tests passing
- [ ] Manual demonstration successful

✅ **Documentation:**
- [ ] PLANNING-SYSTEM-3.0-GUIDE.md accurate
- [ ] Examples updated with real workflow
- [ ] CORTEX.prompt.md reflects correct commands

✅ **SKULL Enforcement:**
- [ ] SKULL-011 (TEMP_PLAN_APPROVAL_ENFORCEMENT) active
- [ ] SKULL-012 (PLAN_PROMOTION_INTEGRITY) active
- [ ] SKULL-013 (CONTEXT_CONTINUITY_ENFORCEMENT) active

---

## 📅 Implementation Timeline

### Week 1 (December 17-19, 2025)
- **Day 1:** Phase 1 - Orchestrator Integration
- **Day 2:** Phase 2 - Iterative Refinement Loop
- **Day 3:** Phase 3 - Plan Generation & Lifecycle

### Week 2 (December 20-21, 2025)
- **Testing & Validation**
- **Documentation Updates**
- **Production Deployment**

---

## 🔗 Related Documents

- **Gap Analysis:** `UNIFIED-PLANNING-GAP-ANALYSIS-IMPLEMENTATION-PLAN.md` (baseline)
- **User Guide:** `cortex-brain/PLANNING-SYSTEM-3.0-GUIDE.md`
- **Orchestrator:** `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml` (lines 3112-3266)
- **Templates:** `cortex-brain/templates/planning/MASTER-PLAN-TEMPLATE.md`

---

**Status:** Ready for Phase 1 implementation  
**Next Action:** Begin orchestrator integration (Phase 1, Task 1)
