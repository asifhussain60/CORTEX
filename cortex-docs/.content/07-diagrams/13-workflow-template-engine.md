# Workflow Template Engine Diagram

---
title: Workflow Template Library — Composition and Execution
type: diagram
audience: [Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex-registry/workflows/templates/
order: 13
---

> How 17 template categories compose from primitives to executable workflows.

## Template Composition Architecture

```
  PRIMITIVES (atomic)                    TEMPLATES (composed)
  ─────────────────                      ────────────────────
  ┌────────────────┐
  │ analysis/      │─┐
  │  ast-scan      │ │
  │  security-scan │ │     ┌───────────────────────────────────┐
  └────────────────┘ │     │  sdlc/                            │
  ┌────────────────┐ ├────▶│    requirements-analysis.yaml     │
  │ validation/    │ │     │    solution-design.yaml           │
  │  detect-fix-   │ │     │    implementation-execution.yaml  │
  │  rescan-loop   │ │     │    testing-strategy.yaml          │
  └────────────────┘ │     │    security-review.yaml           │
  ┌────────────────┐ │     │    deployment-pipeline.yaml       │
  │ governance/    │─┘     │    code-review-checklist.yaml     │
  │  sweep-open    │       └───────────────────────────────────┘
  │  sweep-close   │
  └────────────────┘       ┌───────────────────────────────────┐
  ┌────────────────┐       │  audit/                           │
  │ execution/     │──────▶│    audit-fix-pipeline.yaml        │
  │  tdd-cycle     │       │    convergence-loop.yaml          │
  └────────────────┘       └───────────────────────────────────┘
  ┌────────────────┐
  │ intelligence/  │       ┌───────────────────────────────────┐
  │  lens-pipeline │──────▶│  onboarding/                     │
  └────────────────┘       │    repo-onboarding.yaml          │
                           └───────────────────────────────────┘

  17 total categories · 5 primitive categories · WorkflowEngine executes
```

**Detailed diagram:** `flat-files/diagrams/diagram-18-workflow-template-engine.md`
**Full documentation:** `flat-files/17-workflow-template-library.md`

---

*Source: `cortex-registry/workflows/templates/` · `cortex/core/workflow_engine.py`*
