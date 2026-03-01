---
id: workflow-tdd-cycle-and-fsm
title: TDD cycle and workflow engine FSM
purpose: Show RED→GREEN→REFACTOR and the workflow engine execution states.
audience:
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/core/tdd_orchestrator.py
  - cortex/core/workflow_engine.py
last_verified: 2026-03-01
diagram_type: Workflow
render: ascii
---

# TDD Cycle & Workflow Engine FSM

```
                    ┌──────────────────────────────────────────────────────┐
                    │              TDD CYCLE (CORE-008)                    │
                    │  RED (failing test) → GREEN (minimal code) → REFACTOR│
                    └──────────────────────────────────────────────────────┘

                    ┌──────────────────────────────────────────────────────┐
                    │           WORKFLOW ENGINE FSM                        │
                    │  PENDING → RUNNING → (PASSED | FAILED | BLOCKED)     │
                    └──────────────────────────────────────────────────────┘
```
