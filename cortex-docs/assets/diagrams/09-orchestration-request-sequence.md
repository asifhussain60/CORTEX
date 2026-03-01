---
id: orchestration-request-sequence
title: End-to-end request sequence
purpose: Show a single user request flowing through MCP, orchestration, intelligence, and governance.
audience:
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/core/master_orchestrator.py
  - cortex/mcp/
last_verified: 2026-03-01
diagram_type: Sequence
render: ascii
---

# Data Flow — End-to-End Request Pipeline

```
USER → MCP (JSON-RPC/stdIO) → MasterOrchestrator
  → Intent routing → LENS context → Governance gate → TDD cycle
  → Result returned + audit trail updated
```
