# Complete CORTEX Orchestrator Registry

**Purpose:** Comprehensive registry of ALL orchestrators with execution classification

**Author:** Asif Hussain | **Date:** December 09, 2025

---

## Executive Summary

**Total Orchestrators:** 27 discovered  
**CLI Wrapper Required:** 7 (missing implementations)  
**Copilot Chat:** 6 (correct)  
**Internal:** 14 (infrastructure)

---

## 1. System Operations (CLI Wrapper Required)

### 1.1 Missing CLI Wrappers (❌ PRIORITY)

| Orchestrator | File | Status | Notes |
|--------------|------|--------|-------|
| align | `src/operations/modules/realignment/realignment_utility.py` | ❌ No wrapper | Function exists: `align_system_v2()` |
| optimize | `src/operations/modules/optimization/optimize_cortex_orchestrator.py` | ❌ No wrapper | Class: `OptimizeCortexOrchestrator` |
| healthcheck | `src/operations/healthcheck_operation.py` | ❌ No wrapper | Class: `HealthCheckOperation` |
| review | `src/operations/modules/architectural/review_orchestrator.py` | ❌ No wrapper | Class: `ReviewOrchestrator` |
| cleanup | `src/operations/modules/cleanup/holistic_cleanup_orchestrator.py` | ❌ No wrapper | Class: `HolisticCleanupOrchestrator` |
| deploy | `src/operations/modules/routing/unified_entry_point_utility.py` | ❌ No wrapper | Function: `deploy_cortex()` |
| regenerate_prompts | `scripts/regenerate_cortex_prompts.py` | ❌ No wrapper | Script exists, needs wrapper |

### 1.2 Existing CLI Wrappers (✅ CORRECT)

| Orchestrator | File | Status | Notes |
|--------------|------|--------|-------|
| system_maintenance | `src/operations/modules/orchestration/system_maintenance_orchestrator.py` | ✅ Has wrapper | Reference implementation |
| load_dashboard | `src/dashboard/orchestrator.py` | ✅ Has wrapper | HTTP server pattern |

---

## 2. Interactive Workflows (Copilot Chat)

| Orchestrator | File | Execution | Notes |
|--------------|------|-----------|-------|
| planning_orchestrator | `src/orchestrators/planning_orchestrator.py` | ✅ Chat | Planning System |
| plan_ado | ADO integration in planning | ✅ Chat | Work item creation |
| plan_execution_orchestrator_v2 | `src/orchestrators/plan_execution_orchestrator_v2.py` | ✅ Chat | Autonomous execution |
| tdd_implementation_orchestrator | `src/orchestrators/tdd_implementation_orchestrator.py` | ✅ Chat | TDD workflow |
| feedback | Response template based | ✅ Chat | Feedback collection |
| help | Response template based | ✅ Chat | Command documentation |

---

## 3. Internal Orchestrators (Infrastructure)

### 3.1 Phase 5.1/5.2 - Observer Pattern (NEW)

| Orchestrator | File | Purpose | Phase |
|--------------|------|---------|-------|
| learning_observer | `src/orchestrators/learning_observer.py` | Event-driven pattern capture | 5.1 |
| debug_workflow_orchestrator | `src/orchestrators/debug_workflow_orchestrator.py` | Debug session management, RCA | 5.2 |
| tdd_workflow_orchestrator | `src/workflows/tdd_workflow_orchestrator.py` | TDD orchestration with observer | 5.1 |

**Key:** These orchestrators implement observer pattern and are NOT directly invoked by users. They respond to events from other orchestrators.

### 3.2 Infrastructure Orchestrators

| Orchestrator | File | Purpose |
|--------------|------|---------|
| git_checkpoint_orchestrator | `src/orchestrators/git_checkpoint_orchestrator.py` | Git operations, rollback |
| git_sync_and_optimize | `src/orchestrators/git_sync_and_optimize.py` | Git + optimization combo |
| plan_execution_orchestrator | `src/orchestrators/plan_execution_orchestrator.py` | Plan execution (v1, deprecated) |
| onboarding_acknowledgment_orchestrator | `src/orchestrators/onboarding_acknowledgment_orchestrator.py` | User onboarding |
| manager_report_orchestrator | `src/orchestrators/manager_report_orchestrator.py` | Manager reports |
| documentation_orchestrator | `src/orchestrators/documentation_orchestrator.py` | Doc generation |
| application_health_orchestrator | `src/orchestrators/application_health_orchestrator.py` | Health monitoring |

### 3.3 Hidden System Orchestrators

| Orchestrator | File | Purpose | Recommendation |
|--------------|------|---------|----------------|
| brain_tuning_orchestrator | `src/operations/modules/brain/brain_tuning_orchestrator.py` | Memory optimization | Expose as CLI |
| operations_orchestrator | `src/operations/operations_orchestrator.py` | Operations routing | Keep internal |
| onboarding_orchestrator | `src/operations/onboarding_orchestrator.py` | Onboarding flow | Keep internal |
| setup_orchestrator | `src/setup/setup_orchestrator.py` | Initial setup | Keep internal |

---

## 4. Specialized Orchestrators

### 4.1 Dashboard & Reporting

| Orchestrator | File | Purpose |
|--------------|------|---------|
| dashboard_orchestrator | `src/dashboard/orchestrator.py` | Dashboard server |
| scalable_collector_orchestrator | `src/dashboard/orchestrators/scalable_collector_orchestrator.py` | Data collection |

### 4.2 Intelligence & Analysis

| Orchestrator | File | Purpose |
|--------------|------|---------|
| executive_summary_orchestrator | `src/intelligence/executive_summary_orchestrator.py` | Executive summaries |
| multi_language_docstring_orchestrator | `src/intelligence/multi_language_docstring_orchestrator.py` | Docstring generation |

### 4.3 Utilities

| Orchestrator | File | Purpose |
|--------------|------|---------|
| cleanup_orchestrator (legacy) | `src/plugins/cleanup_orchestrator.py` | Legacy cleanup (use holistic) |
| workflow_orchestrator | `src/workflows/workflow_engine.py` | Generic workflow engine |

---

## 5. Operations Registry Schema Update

### Current Schema (Missing)

```yaml
operations:
  review:
    name: Review
    description: Code Review CLI
    deployment_tier: dual_context
    # ❌ MISSING: execution_method
```

### Required Schema (New)

```yaml
operations:
  review:
    name: Review
    description: Code Review CLI
    deployment_tier: dual_context
    execution_method: cli_wrapper  # ✅ NEW
    cli_script: scripts/cli_wrappers/review_wrapper.py  # ✅ NEW
    natural_language:
      - feature review
      - review new authentication feature
```

### Execution Method Values

| Value | Description | Count | Examples |
|-------|-------------|-------|----------|
| `cli_wrapper` | System operations, file I/O | 9 | align, optimize, healthcheck, review |
| `copilot_chat` | Interactive workflows | 6 | plan, plan ado, start tdd |
| `internal` | Infrastructure, not user-invoked | 14 | learning_observer, debug_workflow |

---

## 6. Phase 5 Observer Pattern Architecture

### Observer Pattern Orchestrators

```
┌─────────────────────────────────────────────────────────────┐
│                    User-Facing Layer                         │
│                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │   Planning    │  │      TDD      │  │     Debug     │  │
│  │ Orchestrator  │  │ Orchestrator  │  │ Orchestrator  │  │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘  │
│          │                   │                   │          │
│          │ emit events       │ emit events       │ emit     │
│          │                   │                   │ events   │
└──────────┼───────────────────┼───────────────────┼──────────┘
           │                   │                   │
           └───────────────────┴───────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  LearningObserver   │  ← Phase 5.1
                    │  (Event Handler)    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Tier 2: KG        │
                    │  (Pattern Storage)  │
                    └─────────────────────┘
```

**Key Points:**
- Observer orchestrators are INTERNAL (not user-invoked)
- execution_method: `internal`
- No CLI wrapper needed
- Called via event emission from user-facing orchestrators

---

## 7. Priority Implementation Order

### Phase 1: Critical CLI Wrappers (Week 1)

1. **align_wrapper.py** - Most frequently used, system validation
2. **healthcheck_wrapper.py** - Diagnostic tool
3. **optimize_wrapper.py** - Performance improvements

### Phase 2: Secondary CLI Wrappers (Week 2)

4. **review_wrapper.py** - Architecture analysis
5. **cleanup_wrapper.py** - Maintenance operations
6. **deploy_wrapper.py** - Production deployment
7. **regenerate_prompts_wrapper.py** - System refresh

### Phase 3: Registry Update (Week 2)

8. Add `execution_method` field to all operations
9. Document Phase 5.1/5.2 orchestrators in registry
10. Update routing logic in entry point

---

## 8. Testing Requirements

### CLI Wrapper Tests

Each wrapper requires:
- ✅ Unit test (mock orchestrator, validate output)
- ✅ Integration test (real orchestrator invocation)
- ✅ Performance test (<3 seconds for system ops)
- ✅ Exit code validation (0 = success, 1 = error)

### Regression Tests

- ✅ All Phase 5 tests (86/86 passing)
- ✅ Chat operations unchanged (plan, start tdd)
- ✅ System maintenance end-to-end
- ✅ Observer pattern functionality

---

## 9. Documentation Updates Required

1. **CORTEX.prompt.md**
   - Add execution_method explanation
   - Document CLI wrapper pattern
   - Update command reference table

2. **cortex-operations.yaml**
   - Add execution_method to all operations
   - Add Phase 5.1/5.2 orchestrator entries
   - Add cli_script paths

3. **Implementation Guides**
   - Create CLI wrapper development guide
   - Document observer pattern usage
   - Update system maintenance guide

---

## 10. Success Criteria

- [ ] All 7 missing CLI wrappers implemented
- [ ] execution_method field on all 150+ operations
- [ ] Phase 5 orchestrators documented in registry
- [ ] Routing logic supports CLI wrapper discovery
- [ ] 100% test pass rate maintained (86/86)
- [ ] No regressions in chat-based operations
- [ ] Performance targets met (<3s for system ops)

---

**Next Steps:** See `ORCHESTRATOR-CLI-WRAPPER-MIGRATION.yaml` for detailed implementation plan.
