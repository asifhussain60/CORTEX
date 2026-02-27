# WorkflowEngine Runtime

---
title: CORTEX WorkflowEngine — YAML→FSM→ConvergenceLoop Runtime (Phase 79-D)
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/workflow/ + cortex-registry/workflows/templates/
phase: Phase 79-D (COMPLETE)
order: 11
---

> **What is it?** The WorkflowEngine is the runtime layer that translates YAML workflow template definitions into executable Finite State Machine (FSM) step graphs, with a convergence loop that guarantees every audit-fix sweep runs until all violations are resolved — not just once.

---

## Why It Exists

Before Phase 79-D, CORTEX had rich YAML workflow templates but no runtime that could:
- Execute templates as typed step graphs (not just YAML parsing)
- Track per-step state transitions (PENDING → RUNNING → PASSED/FAILED)
- Loop detect→fix→rescan until convergence (0 P0/P1 violations)
- Register step handlers by type ID without tight coupling

Phase 79-D delivered all four.

---

## Architecture

```
cortex/orchestrators/workflow/
├── step_state_machine.py       ← FSM: PENDING→RUNNING→CHECKING→PASSED/FAILED/RETRYING/SKIPPED
├── workflow_composer.py        ← Composes YAML → executable step graph + StepHandlerRegistry
├── convergence_loop_executor.py← Retry with exponential backoff + convergence detection
├── template_registry.py        ← Discovers + caches YAML workflow templates
├── workflow_composer.py        ← WorkflowComposer: ConvergenceGate wired as convergence gate
└── workflow_runtime.py         ← End-to-end runtime glue
```

---

## Core Components

### StepStateMachine (`step_state_machine.py`)

A `transitions`-library FSM that governs how each workflow step progresses:

| State | Meaning |
|-------|---------|
| `PENDING` | Step queued, not yet started |
| `RUNNING` | Step actively executing |
| `CHECKING` | ConvergenceNeuron evaluating success criteria |
| `PASSED` | Success criteria met — proceed to next step |
| `RETRYING` | Success criteria NOT met — re-execute (cycle++) |
| `FAILED` | max_cycles exceeded or unrecoverable error |
| `SKIPPED` | Optional step with unmet precondition |

**Convergence Gate Config:**

```python
from cortex.orchestrators.workflow.step_state_machine import ConvergenceGateConfig

config = ConvergenceGateConfig(
    max_cycles=5,
    success_criteria={"all_tests_pass": True, "coverage_target_met": True},
    convergence_predicate="all_tests_pass and coverage >= 0.95",
    scan_function="run_tests_and_measure_coverage",
    backoff_strategy="exponential"  # none | linear | exponential
)
```

---

### StepHandlerRegistry (in `workflow_composer.py`)

Maps step `type` IDs to Python callables. Decouples YAML template definitions from implementation:

```python
from cortex.orchestrators.workflow.workflow_composer import StepHandlerRegistry

registry = StepHandlerRegistry()
registry.register("run_tests", my_test_runner_fn)
registry.register("lint_check", my_lint_fn)
```

When `WorkflowComposer` processes a YAML step with `type: run_tests`, it looks up `my_test_runner_fn` in the registry and executes it. Unknown types raise `UnregisteredStepTypeError`.

---

### ConvergenceLoopExecutor (`convergence_loop_executor.py`)

Implements the detect→fix→rescan loop primitive with exponential backoff:

```python
from cortex.orchestrators.workflow.convergence_loop_executor import (
    ConvergenceLoopExecutor, ConvergenceConfig
)

config = ConvergenceConfig(
    max_retries=5,
    initial_backoff_seconds=1.0,
    backoff_multiplier=2.0,
    max_backoff_seconds=60.0,
    timeout_seconds=300.0
)

executor = ConvergenceLoopExecutor(config=config)
result = executor.execute(
    fn=audit_and_fix,
    convergence_check=lambda r: r.p0_count == 0 and r.p1_count == 0
)

# result.converged → True when 0 P0/P1 violations
# result.attempts  → number of iterations taken
# result.duration_seconds → total wall-clock time
```

**Convergence guarantee (CORE-064):** The loop continues until `convergence_check` returns `True`. There is no single-pass mode — partial sweeps are architecturally prevented.

---

### TemplateRegistry (`template_registry.py`)

Discovers all YAML workflow templates in `cortex-registry/workflows/templates/` and makes them available by ID:

```python
from cortex.orchestrators.workflow.template_registry import TemplateRegistry

registry = TemplateRegistry()
template = registry.get("audit/audit-fix-pipeline")
# Returns parsed YAML dict with steps, convergence_gate, metadata
```

Templates are cached with 5-minute TTL and auto-reloaded on file change (dev mode).

---

## Integration: Convergence Gate in TDD + Audit Templates

Phase 79-D-D added `convergence_gate` blocks to the canonical TDD and audit YAML templates:

```yaml
# cortex-registry/workflows/templates/tdd/tdd-red-green-refactor.yaml
convergence_gate:
  type: detect-fix-rescan-loop
  scan_function: run_failing_tests
  success_criteria:
    all_tests_pass: true
    coverage_target_met: true
  max_cycles: 10
  backoff_strategy: exponential
```

```yaml
# cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml
convergence_gate:
  type: detect-fix-rescan-loop
  scan_function: count_p0_p1_violations
  success_criteria:
    p0_count: 0
    p1_count: 0
  max_cycles: 20
  backoff_strategy: linear
```

When `WorkflowComposer` builds the step graph, it detects the `convergence_gate` block and wires `ConvergenceLoopExecutor` as the execution wrapper for the affected stages.

---

## AuditFix Pipeline Integration (Stages 7–8)

The convergence loop is the engine behind `/audit fix` Stages 7–8:

```
Stage 7: Auto-Fix Convergence Loop (detect-fix-rescan-loop primitive)
   └── ConvergenceLoopExecutor.execute(
           fn=audit_and_fix_all_violations,
           convergence_check=lambda r: r.p0_count == 0 and r.p1_count == 0
       )
       ├── Iteration 1: Detect → N violations → Fix → Rescan
       ├── Iteration 2: Detect → M violations → Fix → Rescan  (M < N)
       └── Iteration K: Detect → 0 P0/P1 → converged=True ✅

Stage 8: Final convergence verification + AC_COMPLETE log
```

**Why this matters:** Before Phase 79-D, audit-fix was a single pass. You could run `/audit fix` and still have residual violations because fixes introduced new ones. The convergence loop eliminates this — it keeps going until the system is clean.

---

## Live Location Summary

| Artifact | Path |
|---------|------|
| StepStateMachine | `cortex/orchestrators/workflow/step_state_machine.py` |
| WorkflowComposer + StepHandlerRegistry | `cortex/orchestrators/workflow/workflow_composer.py` |
| ConvergenceLoopExecutor | `cortex/orchestrators/workflow/convergence_loop_executor.py` |
| TemplateRegistry | `cortex/orchestrators/workflow/template_registry.py` |
| Detect-Fix-Rescan primitive | `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml` |
| AuditFix pipeline template | `cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml` |
| TDD template (with gate) | `cortex-registry/workflows/templates/tdd/tdd-red-green-refactor.yaml` |
| Phase 79-D detail | `cortex-registry/planning/phases/completed/phase-67.yaml` |

---

## Audience Perspectives

**Business Leader:** "The convergence loop is our quality guarantee. When developers run the audit-fix pipeline, it doesn't stop after one pass — it keeps fixing issues until the system is clean. No shortcuts, no partial fixes shipped."

**Product Owner:** "I can see exactly how many loop iterations it took to reach convergence in the audit log. If it's taking 10+ iterations consistently, that signals a systemic code quality issue to investigate."

**Developer:** "The StepHandlerRegistry means I can add new step types to YAML templates without modifying WorkflowComposer. I `registry.register('my_step', my_fn)` and the runtime picks it up automatically."

---

*Phase 79-D COMPLETE — all 6 GAPs closed (GAP-67-A through GAP-67-F) · Verified 2026-02-25*
