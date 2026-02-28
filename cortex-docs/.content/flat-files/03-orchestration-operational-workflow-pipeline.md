# Operational Workflow Pipeline

---
title: Operational Workflow Pipeline — Technology Routing, Template Engagement, and Visual Tracing
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/workflow/ + cortex/orchestrators/core/intent_router/workflow_gate.py
order: 16
synced_from: 03-orchestration/16-operational-workflow-pipeline.md
---

> **The central idea:** Workflow templates are not just documentation — they are executable specifications that route through technology-aware gates, bind to the correct execution strategy, and emit visual traces to SQLite for auditability.

---

## What Phase 89 Delivered

Phase 89 (Operational Workflow Pipeline) wired the complete workflow infrastructure from inert YAML definitions to live, executable pipelines. Seven capability clusters were addressed:

### A. Technology-Aware Routing

`WorkflowComplexityRouter` at `cortex/orchestrators/core/intent_router/workflow_gate.py` evaluates incoming requests against the technology stack detected by LENS. A C# refactoring request routes to the `csharp-refactor-workflow.yaml` template; a Python TDD request routes to `tdd-feature-implementation.yaml`. The router uses LENS language detection plus template tag matching.

### B. PostRefactorLintGate

After every refactoring operation, a lint gate runs automatically to verify the refactored code is clean. This prevents the common pattern of refactoring introducing lint regressions that are not caught until the next audit.

### C. Engagement Visibility

All workflow operations now emit engagement signals via EngagementRenderer — breadcrumbs showing which template is active, which step is executing, and estimated remaining time.

### D. SQLite Tracing

Every workflow step emits AC markers to `.cortex-runtime/traces/orchestrator-traces.db`, creating a complete audit trail of template-to-step-to-outcome for each workflow execution.

### E. Template Wiring

The `_check_for_workflow_template()` method in MasterOrchestrator was expanded from six to twenty operation types, ensuring all intent types that have associated workflow templates are correctly bound.

---

## Workflow Template Categories (79 Templates)

The complete template library lives at `cortex-registry/workflows/templates/` across seventeen categories:

| Category | Templates | Purpose |
|----------|-----------|---------|
| audit | 1 | Audit-fix pipeline |
| backend | 2 | C# refactor and security |
| composites | 7 | Multi-template pipelines |
| debugging | 1 | Multi-stack debug (8 strategies) |
| frontend | 4 | CSS, HTML, TypeScript |
| governance | 6 | Phase lifecycle, golden test promotion |
| intelligence | 4 | Intelligence matrix, RCA |
| internal | 2 | Docs refresh, site validation |
| lifecycle | 7 | Onboarding, migration, release |
| maintenance | 5 | Cleanup, dedup, flat-file sync |
| primitives | 11 | Atomic building blocks |
| quality | 6 | Code quality, refactor sweep |
| rca | 1 | Root cause analysis |
| sdlc | 7 | Requirements to release lifecycle |
| security | 3 | Compliance, hardening, threat models |
| tdd | 5 | TDD workflows (API, frontend, feature) |
| testing | 2 | Test quality, tier manifest |

---

## Workflow Composer

`WorkflowComposer` at `cortex/orchestrators/workflow/workflow_composer.py` is the engine that:

1. **Reads** YAML template definitions from the registry
2. **Resolves** template dependencies (composite templates reference atomic primitives)
3. **Composes** an executable step graph with typed step handlers
4. **Binds** the convergence gate (CORE-068) as the terminal validation
5. **Executes** the graph via StepStateMachine with FSM state tracking

The Workflow Composer is the primary integration point between YAML-defined workflows and the live Python orchestrator runtime.

---

## WorkflowGateway — Mandatory Entry Point (Phase 94–99)

Phase 94 introduced `WorkflowGateway` at `cortex/orchestrators/workflow/workflow_gateway.py` with the `@enforce_gateway` decorator. All Category A orchestrators (TDDOrchestrator, RefactoringOrchestrator, DebuggerOrchestrator, SecurityVulnerabilityOrchestrator, and others) now route through the gateway before execution.

The gateway ensures:
- **Template resolution** — verifies a matching workflow template exists for the operation
- **Governance pre-flight** — runs the holistic validation gate primitive
- **Convergence binding** — attaches the CORE-068 detect-fix-rescan loop

Phase 96 removed legacy `PHASE90_GATEWAY_ENABLED=False` scaffolding. Phase 98 cleaned up 24 dead workflow modules (reducing `cortex/orchestrators/workflow/` from 29 to 6 files) and 23 unreferenced YAML templates. Phase 99 repaired five fatal breaks in the gateway→composer→template chain.

---

*Verified against workflow_composer.py, workflow_gate.py, and Phase 89 wiring*
