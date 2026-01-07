---
title: Master Orchestrator
---

The Master Orchestrator is the entry point. It:

1. Parses intent and context.
2. Calls the Governance Merger to produce (or load) the Unified Instruction Set.
3. Uses the Pattern Router to route to the correct workflow orchestrator.
4. Calls the TODO Orchestrator to generate a DAG of work.
5. Ensures all operations are audit-logged and resource-limited.
6. Coordinates checkpoints and rollback.

Think of it as “policy-aware conductor,” not a code generator.
