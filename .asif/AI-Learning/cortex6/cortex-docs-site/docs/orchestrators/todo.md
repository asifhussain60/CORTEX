---
title: TODO Orchestrator (DAG)
---

The TODO Orchestrator builds a **Directed Acyclic Graph** of tasks:

- Nodes: TODOs generated from governance + workflow steps
- Edges: dependencies (e.g., tests before implementation)
- Validation: detect cycles, enforce constraints
- Optimization: identify tasks that can run in parallel
- Resilience: checkpoint every N tasks, rollback on triggers

This is how CORTEX makes execution deterministic and safe.
