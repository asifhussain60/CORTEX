# Cross-Orchestrator Communication

---
title: Cross-Orchestrator Communication
type: reference
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/core/master_orchestrator.py
order: 6
---

## How Orchestrators Communicate

Orchestrators don't call each other directly. All communication flows through **MasterOrchestrator**:

```
[Orchestrator A] ─── result ──→ [MasterOrchestrator] ─── dispatch ──→ [Orchestrator B]
```

This ensures:
1. All inter-orchestrator communication is auditable
2. Governance gates are checked between orchestrator handoffs
3. No circular dependencies between orchestrators
4. The audit trail captures the complete request path

## Common Communication Patterns

| Pattern | Example |
|---------|---------|
| **Sequential** | IntentRouter → TDDOrchestrator → EnforcementOrchestrator |
| **Fan-out** | MasterOrchestrator dispatches to multiple analyzers |
| **Callback** | Orchestrator requests LENS analysis mid-execution |
| **Pipeline** | RequestRephrase → Intent → TDD → Governance → Audit |

---

*Verified against orchestrator dispatch patterns · 25 February 2026*
