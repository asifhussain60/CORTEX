---
title: Components
---

At minimum, the system includes:

- **Master Orchestrator**: entry point; orchestrates governance, routing, TODO generation and execution.
- **Governance Merger**: merges 4 governance sources into the unified instruction set.
- **Pattern Router**: O(1) routing using a Trie.
- **TODO Orchestrator**: builds and executes a DAG of tasks.
- **Workflow Orchestrators**: Planning, TDD, ADO, Vacuum, Cleanup, Investigation, Sanitization, Debug, Refinement, Maintenance.
- **State Manager**: SQLite WAL + optimistic locking for concurrency.
- **Checkpoint / Rollback**: recovery and resilience primitives.
- **Audit Logger**: runtime enforcement; cannot be bypassed.
- **Resource Limiter**: quotas and guardrails.

As the implementation grows, this page becomes the canonical “component index.”
