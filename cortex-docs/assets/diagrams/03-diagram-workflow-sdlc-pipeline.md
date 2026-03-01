---
id: workflow-sdlc-pipeline
title: SDLC workflow pipeline (7 phases)
purpose: Show the full SDLC pipeline and how workflow templates execute with gates.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex-registry/workflows/templates/sdlc/
  - cortex/orchestrators/domain/
last_verified: 2026-03-01
diagram_type: Workflow
render: ascii
---

# SDLC Workflow Pipeline — 7-Phase Lifecycle

```
 ═══════════════════════════════════════════════════════════════════════════════
  CORTEX SDLC WORKFLOW ENGINE — 7-PHASE PIPELINE
 ═══════════════════════════════════════════════════════════════════════════════

 ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
 │    1.    │  │    2.    │  │    3.    │  │    4.    │  │    5.    │  │    6.    │  │    7.    │
 │REQUIRE- │─▶│SOLUTION  │─▶│IMPLEMENT │─▶│  CODE   │─▶│INTEGRA- │─▶│SECURITY │─▶│ RELEASE │
 │ MENTS   │  │ DESIGN   │  │ ATION    │  │ REVIEW  │  │  TION   │  │ ASSESS  │  │READINESS│
 │ANALYSIS │  │          │  │          │  │  GATE   │  │ VERIFY  │  │  MENT   │  │         │
 └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
      │              │              │              │              │              │              │
   🔒 GATE        🔒 GATE        🔒 GATE        🔒 GATE        🔒 GATE        🔒 GATE        🔒 GATE
```

Also includes knowledge hydration (company overrides win) and a workflow FSM (pending → running → completed / failed / blocked).
