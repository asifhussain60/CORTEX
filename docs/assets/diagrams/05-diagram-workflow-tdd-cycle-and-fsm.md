---
id: workflow-tdd-cycle-and-fsm
title: TDD cycle and workflow engine FSM
purpose: Show how CORTEX enforces test-driven development with state machines governing every code change.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/core/tdd_orchestrator.py
  - cortex-registry/workflows/templates/sdlc/implement-workflow.yaml
last_verified: 2026-03-03
diagram_type: Workflow
render: ascii
render_html: true
d3_method: "d3.tree() — cycle diagram (RED-GREEN-REFACTOR) + state machine"
---

# TDD Cycle & Workflow Engine FSM

## TDD Cycle (CORE-008 — Mandatory for ALL Code Changes)

```
    ┌─────────────────────────────────────────────────────────────────────────┐
    │                    TDD CYCLE (CORE-008)                                 │
    │                                                                         │
    │   ┌──────────┐      ┌──────────┐      ┌──────────┐                     │
    │   │   RED    │      │  GREEN   │      │ REFACTOR │                     │
    │   │          │─────▶│          │─────▶│          │                     │
    │   │ Write    │      │ Minimal  │      │ Clean up │                     │
    │   │ failing  │      │ code to  │      │ without  │                     │
    │   │ test     │      │ pass     │      │ changing │                     │
    │   │ FIRST    │      │ tests    │      │ behavior │                     │
    │   └──────────┘      └──────────┘      └──────────┘                     │
    │        │                  │                  │                           │
    │     🔒 GATE           🔒 GATE            🔒 GATE                       │
    │   "All listed       "All tests         "Zero new                       │
    │    tests FAIL"       PASS"              regressions"                    │
    │                                                                         │
    │   Implementation     Refactoring         Marking complete               │
    │   code FORBIDDEN     FORBIDDEN           FORBIDDEN                      │
    │   until gate passes  until gate passes   until gate passes              │
    └─────────────────────────────────────────────────────────────────────────┘
```

**Business impact:** No untested code reaches production. Every change is provably correct.

## Workflow Engine FSM — Execution States

```
                      ┌──────────────────────────────────────────────────┐
                      │           WORKFLOW ENGINE FSM                     │
                      │                                                  │
                      │   ┌─────────┐                                    │
                      │   │ PENDING │ ─── prerequisites not met          │
                      │   └────┬────┘                                    │
                      │        │ all prerequisites satisfied              │
                      │        ▼                                          │
                      │   ┌─────────┐                                    │
                      │   │ RUNNING │ ─── executing workflow steps       │
                      │   └────┬────┘                                    │
                      │        │                                          │
                      │   ┌────┼─────────────┐                           │
                      │   │    │             │                           │
                      │   ▼    ▼             ▼                           │
                      │ ┌──────┐ ┌────────┐ ┌─────────┐                  │
                      │ │PASSED│ │ FAILED │ │ BLOCKED │                  │
                      │ │  ✅  │ │   ❌   │ │   ⛔    │                  │
                      │ └──────┘ └────┬───┘ └────┬────┘                  │
                      │               │          │                       │
                      │               ▼          ▼                       │
                      │         Convergence   Requires                   │
                      │         gate retries  user override              │
                      │         (max 3)       to unblock                 │
                      └──────────────────────────────────────────────────┘
```

**Key insight:** BLOCKED is not FAILED. It means a governance gate prevented unsafe code — resolution is required before progress.
