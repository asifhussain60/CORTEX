---
id: workflow-template-engine
title: Workflow template engine (primitives → templates → composites)
purpose: Explain how CORTEX composes repeatable workflows from YAML primitives.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex-registry/workflows/templates/
  - cortex/core/workflow_engine.py
last_verified: 2026-03-01
diagram_type: Workflow
render: ascii
---

# Workflow Template Engine — Composition and Execution

```
PRIMITIVES (atomic)  →  TEMPLATES (composed)  →  COMPOSITES (pipelines)

Execution:
- load YAML template
- resolve knowledge context
- run steps through WorkflowEngine FSM
- optional convergence loop: detect → fix → rescan
```
