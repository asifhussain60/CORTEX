# Planning v5 + TaskListOrchestrator Pilot Integration

**Date:** January 5, 2026  
**Author:** Asif Hussain  
**Status:** 🚀 **IN PROGRESS**

---

## 🎯 Objective

Retrofit Planning Orchestrator v5 to use TaskListOrchestrator for:
1. **State management** - Replace ad-hoc phase tracking with structured task list
2. **Recovery** - Enable resume from any phase interruption
3. **Progress tracking** - Real-time visibility into planning progress
4. **Checkpointing** - Strategic savepoints before risky operations

---

## 📋 Current Planning v5 Flow

**Phases (5 total):**
1. **Phase 0:** Parse request + create plan in DB
2. **Phase 1:** Context Discovery (workspace search)
3. **Phase 2:** Architecture Analysis (AST scanning)
4. **Phase 3:** Plan Generation (template rendering)
5. **Phase 4:** Folder Creation + Validation

**Current State Management:** BaseOrchestratorV4_1 (phase-based state machine)

---

## 🔄 Integration Strategy

### Option A: Wrapper Integration (Non-Invasive)

**Concept:** Keep BaseOrchestratorV4_1, add TaskListOrchestrator as secondary state tracker

**Pros:**
- ✅ No breaking changes to existing code
- ✅ Easy rollback if issues found
- ✅ Gradual migration path

**Cons:**
- ⚠️ Dual state management (complexity)
- ⚠️ Partial benefits (can't replace base class logic)

### Option B: Direct Integration (Recommended)

**Concept:** Replace BaseOrchestratorV4_1 phase management with TaskListOrchestrator

**Pros:**
- ✅ Full TaskListOrchestrator benefits (sub-ms recovery)
- ✅ Cleaner architecture (single state source)
- ✅ Better long-term maintainability

**Cons:**
- ⚠️ Requires refactoring execute() method
- ⚠️ Needs comprehensive testing

**Decision:** **Option B** (direct integration) - Full benefits justify refactoring cost

---

## 🏗️ Implementation Plan

### Phase 1: Task Definition (30 min)

Map Planning v5 phases to TaskListOrchestrator tasks:

```python
# Planning v5 → TaskListOrchestrator mapping
tasks = [
    {
        "task_id": "parse_request",
        "description": "Parse user request and create plan in DB",
        "executor": self._phase_parse_request,
        "checkpoint_before": False  # Fast operation
    },
    {
        "task_id": "discover_context",
        "description": "Search workspace for relevant context",
        "executor": self._phase_discover_context,
        "checkpoint_before": True,  # ✅ Strategic checkpoint (slow search)
        "depends_on": ["parse_request"]
    },
    {
        "task_id": "analyze_architecture",
        "description": "AST scanning and architecture analysis",
        "executor": self._phase_analyze_architecture,
        "checkpoint_before": False,
        "depends_on": ["discover_context"]
    },
    {
        "task_id": "generate_plan",
        "description": "Render plan from templates",
        "executor": self._phase_generate_plan,
        "checkpoint_before": True,  # ✅ Strategic checkpoint (complex generation)
        "depends_on": ["analyze_architecture"]
    },
    {
        "task_id": "create_folders",
        "description": "Create folder structure",
        "executor": self._phase_create_folders,
        "checkpoint_before": False,
        "depends_on": ["generate_plan"]
    },
    {
        "task_id": "validate_plan",
        "description": "Run validation checks",
        "executor": self._phase_validate,
        "checkpoint_before": False,
        "depends_on": ["create_folders"]
    }
]
```

**Strategic Checkpoints:**
- ✅ Before `discover_context` - Search can be slow (10+ seconds)
- ✅ Before `generate_plan` - Complex template rendering

### Phase 2: Executor Adaptation (45 min)

Convert existing phase methods to task executors:

**Current signature (BaseOrchestratorV4_1):**
```python
def execute_phase(self, phase_number: int, phase_config: dict, **kwargs) -> PhaseResult
```

**New signature (TaskListOrchestrator):**
```python
def _phase_discover_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Task executor for context discovery.
    
    Args:
        params: Task parameters (user_request, plan_id, etc.)
    
    Returns:
        Task result dict (discovered_files, semantic_results, etc.)
    """
    # Extract from params
    user_request = params["user_request"]
    plan_id = params["plan_id"]
    
    # Execute phase logic
    result = self._discover_context_impl(user_request)
    
    # Return dict (serializable)
    return {
        "discovered_files": result.discovered_files,
        "semantic_results": result.semantic_results,
        "status": "completed"
    }
```

### Phase 3: execute() Method Refactoring (30 min)

Replace phase loop with TaskListOrchestrator:

**Before:**
```python
def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
    # Phase 0
    plan_id = self._create_plan(user_request)
    
    # Phase 1
    context = self._discover_context(user_request)
    
    # Phase 2
    analysis = self._analyze_architecture(context)
    
    # ... etc
```

**After:**
```python
def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
    # Create TaskListOrchestrator
    task_orch = TaskListOrchestrator(
        orchestrator_id=f"planning-{self.plan_id}",
        state_db=self.state_db
    )
    
    # Define tasks
    self._define_planning_tasks(task_orch, user_request)
    
    # Execute all
    try:
        task_orch.execute_all()
        return self._build_success_result(task_orch)
    except Exception as e:
        return self._build_failure_result(task_orch, e)
```

### Phase 4: Recovery Testing (15 min)

**Test Scenario:** Interrupt during Phase 2 (Architecture Analysis), then recover

```python
def test_planning_v5_recovery():
    # Start planning
    orch = PlanningOrchestratorV5()
    orch.execute("plan user authentication")
    
    # Simulate interruption during Phase 2
    # ... system crashes ...
    
    # Recovery
    recovered_orch = PlanningOrchestratorV5(resume=True)
    recovered_orch.recover_and_continue()
    
    # Verify: Phases 0-1 completed, Phase 2+ re-executed
    assert recovered_orch.get_progress()["completed"] >= 2
```

---

## 📊 Expected Benefits

| Metric | Before | After (Expected) | Improvement |
|--------|--------|------------------|-------------|
| **Recovery Time** | N/A (no recovery) | <1ms | ✅ New capability |
| **Resume Capability** | Manual (error-prone) | Automatic | ✅ New capability |
| **Progress Visibility** | Phase-level | Task-level | ✅ Finer granularity |
| **Checkpoint Overhead** | N/A | <1ms per checkpoint | ✅ Negligible |
| **Memory Overhead** | Baseline | +0.24KB | ✅ Negligible |

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking changes to BaseOrchestratorV4_1** | High | Create PlanningOrchestratorV5_1 (new class) |
| **Serialization issues with complex results** | Medium | Use JSON-serializable dicts only |
| **Recovery test failures** | Medium | Comprehensive test suite (10+ scenarios) |
| **Performance regression** | Low | Benchmark before/after (expect <1ms overhead) |

---

## ✅ Acceptance Criteria

1. **All 5 phases execute successfully** with TaskListOrchestrator
2. **Recovery works** from any phase interruption (<1ms)
3. **Progress tracking** shows real-time task completion
4. **Checkpoints created** at strategic points (2 total)
5. **No performance regression** (<1ms overhead vs baseline)
6. **All existing tests pass** (0 failures)

---

## 🚀 Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1: Task Definition** | 30 min | Map phases → tasks, define dependencies |
| **Phase 2: Executor Adaptation** | 45 min | Convert phase methods to task executors |
| **Phase 3: execute() Refactoring** | 30 min | Replace phase loop with TaskListOrchestrator |
| **Phase 4: Recovery Testing** | 15 min | Test interruption + recovery scenarios |

**Total:** 2 hours

---

## 📝 Next Steps

1. **Create PlanningOrchestratorV5_1 class** (preserve v5 for rollback)
2. **Implement task definitions** (6 tasks)
3. **Refactor execute() method** (use TaskListOrchestrator)
4. **Write recovery tests** (10+ scenarios)
5. **Benchmark performance** (before/after comparison)
6. **Update documentation** (migration guide)

---

**Status:** Ready to implement - Awaiting approval to proceed with Phase 1
