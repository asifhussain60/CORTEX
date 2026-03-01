---
id: orchestration-request-sequence
title: End-to-end request sequence
purpose: Show a single user request flowing through the 4-stage pipeline with decision points, governance gates, and audit trail.
audience:
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/core/master_orchestrator.py
  - cortex/orchestrators/core/intent_router.py
  - cortex/mcp/
last_verified: 2026-03-01
diagram_type: Sequence
render: ascii
---

# End-to-End Request Sequence — 4-Stage Pipeline

```
 USER                MCP Gateway         MasterOrchestrator        Domain Orch.       Governance
  │                      │                      │                      │                  │
  │  "fix the auth bug"  │                      │                      │                  │
  │─────────────────────▶│                      │                      │                  │
  │                      │  JSON-RPC (stdio)    │                      │                  │
  │                      │─────────────────────▶│                      │                  │
  │                      │                      │                      │                  │
  │                      │              ┌───────┴───────┐              │                  │
  │                      │              │  STAGE 1:     │              │                  │
  │                      │              │  INTERACTION  │              │                  │
  │                      │              │  Comprehend + │              │                  │
  │                      │              │  DoR display  │              │                  │
  │                      │              └───────┬───────┘              │                  │
  │                      │                      │                      │                  │
  │                      │              ┌───────┴───────┐              │                  │
  │                      │              │  STAGE 2:     │              │                  │
  │                      │              │  INTENT       │              │                  │
  │                      │              │  IntentRouter │              │                  │
  │                      │              │  → FIX (0.92) │              │                  │
  │                      │              └───────┬───────┘              │                  │
  │                      │                      │                      │                  │
  │                      │              ┌───────┴───────┐              │                  │
  │                      │              │  STAGE 3:     │              │                  │
  │                      │              │  INTELLIGENCE │              │                  │
  │                      │              │  LENS prefetch│              │                  │
  │                      │              │  (git + AST)  │              │                  │
  │                      │              └───────┬───────┘              │                  │
  │                      │                      │                      │                  │
  │                      │                      │  Holistic Validation │                  │
  │                      │                      │─────────────────────────────────────────▶│
  │                      │                      │                      │    CORE-048 gate  │
  │                      │                      │◀─────────────────────────────────────────│
  │                      │                      │         PASS ✅      │                  │
  │                      │                      │                      │                  │
  │                      │              ┌───────┴───────┐              │                  │
  │                      │              │  STAGE 4:     │              │                  │
  │                      │              │  EXECUTION    │──────────────▶│                  │
  │                      │              │  Delegate to  │   TDD Cycle  │                  │
  │                      │              │  TDDOrch.     │   RED→GREEN  │                  │
  │                      │              │               │   →REFACTOR  │                  │
  │                      │              │               │◀─────────────│                  │
  │                      │              └───────┬───────┘              │                  │
  │                      │                      │                      │                  │
  │                      │                      │  AC_COMPLETE + audit │                  │
  │                      │                      │─────────────────────────────────────────▶│
  │                      │                      │                      │   SQLite trace   │
  │                      │◀─────────────────────│                      │                  │
  │◀─────────────────────│  Result + inline     │                      │                  │
  │                      │  audit summary       │                      │                  │
```

**Key insight:** Every request passes through all 4 stages. Governance validates before execution, never after. The audit trail is written at every stage boundary.
