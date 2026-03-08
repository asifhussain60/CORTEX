---
id: workflow-template-engine
title: Workflow template engine (primitives → templates → composites)
purpose: Explain the 3-tier declarative workflow system that makes every CORTEX operation repeatable and auditable.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex-registry/workflows/templates/
  - cortex/orchestrators/workflow/workflow_composer.py
  - cortex/orchestrators/workflow/template_composer.py
last_verified: 2026-03-03
diagram_type: Workflow
render: ascii
render_html: true
d3_method: "d3.tree() — 3-tier composition hierarchy"
---

# Workflow Template Engine — 3-Tier Composition

```
 ═══════════════════════════════════════════════════════════════════════════════
  TIER 1: PRIMITIVES (atomic, reusable steps)
 ═══════════════════════════════════════════════════════════════════════════════

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ ac-marker-   │  │ holistic-    │  │ detect-fix-  │  │ git-         │
  │ emit.yaml    │  │ validation-  │  │ rescan-      │  │ checkpoint   │
  │              │  │ gate.yaml    │  │ loop.yaml    │  │ .yaml        │
  │ AC_START/    │  │ CORE-048     │  │ CORE-068     │  │ rollback     │
  │ AC_COMPLETE  │  │ risk check   │  │ convergence  │  │ safety       │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │                 │
 ════════╪═════════════════╪═════════════════╪═════════════════╪════════════════
  TIER 2: MODE WORKFLOWS (one per execution mode)
 ═══════════════════════════════════════════════════════════════════════════════

  ┌───────────────────────────────────────────────────────────────────────┐
  │  implement-workflow.yaml                                              │
  │                                                                       │
  │  steps:                                                               │
  │    1. inject: holistic-validation-gate.yaml  ──── CORE-048            │
  │    2. inject: challenge-gate.yaml            ──── risk > 0.4?         │
  │    3. inject: sweep-catalogue-open.yaml      ──── CORE-064            │
  │    4. execute: RED → GREEN → REFACTOR        ──── CORE-008            │
  │    5. inject: detect-fix-rescan-loop.yaml    ──── CORE-068            │
  │    6. inject: sweep-catalogue-close.yaml     ──── verify all closed   │
  │    7. inject: ac-marker-emit.yaml            ──── audit trail         │
  │    8. inject: git-checkpoint.yaml            ──── safe commit         │
  └───────────────────────────────────────────────────────────────────────┘

  Similar templates: fix-workflow.yaml · refactor-workflow.yaml · vacuum-workflow.yaml

 ═══════════════════════════════════════════════════════════════════════════════
  TIER 3: COMPOSITE PIPELINES (multi-mode orchestrations)
 ═══════════════════════════════════════════════════════════════════════════════

  ┌───────────────────────────────────────────────────────────────────────┐
  │  audit-fix-pipeline.yaml                                              │
  │                                                                       │
  │  composes: environment-readiness → governance-preflight → 20-point    │
  │            scan → wiring-validation → health-check → vacuum →         │
  │            meta-audit → auto-fix-convergence → tests + AC_COMPLETE    │
  │                                                                       │
  │  convergence: loops stages 7-8 until P0=0 AND P1=0                   │
  └───────────────────────────────────────────────────────────────────────┘

  Similar composites: totalrecall-workflow.yaml · multi-stack-debug-pipeline.yaml
```

## Execution Flow

```
  IntentRouter classifies → IMPLEMENT
          │
          ▼
  WorkflowGateway.resolve_template("IMPLEMENT")
          │
          ▼
  Loads: sdlc/implement-workflow.yaml
          │
          ▼
  TemplateComposer injects primitives at marked positions
          │
          ▼
  WorkflowComposer executes step-by-step through FSM
          │
          ├─── Each step: PENDING → RUNNING → PASSED/FAILED/BLOCKED
          │
          ▼
  On convergence_mode=True: detect→fix→rescan loop (max 3 cycles)
          │
          ▼
  AC_COMPLETE → SQLite trace → result returned
```

**Business impact:** Every operation follows a declared, auditable template. No ad-hoc execution. Workflows are configuration, not code — changeable without deployments.
