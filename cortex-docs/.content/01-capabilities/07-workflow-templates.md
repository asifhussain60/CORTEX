# Workflow Templates

---
title: CORTEX Workflow Templates — Reusable Execution Patterns
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex-registry/workflows/templates/ + cortex/core/workflow_engine.py
order: 7
---

> **Brain analogy:** Workflow templates are **motor programs** — pre-learned sequences of actions (like riding a bicycle) that the brain can execute without conscious planning each step. Once learned, they execute reliably every time.

---

## Template Architecture

Workflow templates are YAML files stored in `cortex-registry/workflows/templates/` and executed by the WorkflowEngine (`cortex/core/workflow_engine.py`).

### Two Categories

| Category | Location | Purpose |
|----------|----------|---------|
| **lifecycle/** | `cortex-registry/workflows/templates/lifecycle/` | CORTEX-internal workflows (phase execution, master plan) |
| **production/** | `cortex-registry/workflows/templates/production/` | External production workflows (deployment, rollback) |

---

## Lifecycle Templates (CORTEX-Internal)

### MasterPlanOrchestrator Workflow
Creates and manages multi-phase execution plans (like the 12-phase Cohesive Brain Refactor).

**Implementation:** `cortex/orchestrators/core/master_plan_orchestrator.py` (526 lines)

### MasterPlanExecution Workflow
LENS discovery + multi-phase execution with validation loops.

### PhaseExecutor Workflow
Reusable RED → GREEN → REFACTOR → CLEANUP pattern for individual phases.

---

## How Templates Work

```
[WorkflowEngine reads YAML template]
        │
        ▼
[Parse phases and dependencies]
        │
        ▼
[Execute phases sequentially]
        │
        ├── For each phase:
        │   ├── setup()
        │   ├── govern() ← governance gate
        │   ├── execute() ← RED → GREEN → REFACTOR
        │   ├── validate() ← acceptance criteria
        │   └── teardown() ← audit trail
        │
        ▼
[Validation loop — retry if needed]
        │
        ▼
[Complete — update cortex-registry status]
```

---

## Practical Examples

**Business Leader:** "The 12-phase refactor was orchestrated by workflow templates. Each phase followed the same pattern: plan, test, implement, validate. 683 tests passing, zero regression."

**Product Owner:** "I can see the workflow template for any phase. It specifies entry conditions, deliverables, exit gates, and rollback criteria. No ambiguity about what 'done' means."

**Developer:** "I define a new workflow template in YAML, register it in `cortex-registry/workflows/templates/`, and WorkflowEngine can execute it. The PhaseExecutor template handles TDD automatically."

---

*Verified against workflow template registry · 25 February 2026*
