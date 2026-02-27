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

*Verified against orchestrator dispatch patterns*

---

## Orchestrator Engagement Visibility

Every orchestrator invocation emits engagement signals so users understand which orchestrator is active and why.

### BLOCK-ENGAGEMENT-BREADCRUMB

Rendered on every response header for multi-hop routing chains:

```
**Route:** `IntentRouter → MasterOrchestrator → TDDOrchestrator`
```

This is the primary engagement signal — always rendered, never omitted for 2+ hop chains.

### BLOCK-ENGAGEMENT-TIMELINE

Collapsible timing log emitted after 3+ step operations:

| Orchestrator | Duration | Status |
|---|---|---|
| IntentRouter | 0.3s | ✅ |
| MasterOrchestrator | 1.2s | ✅ |
| TDDOrchestrator | 8.4s | ✅ |
| **Total** | **9.9s** | ✅ |

Always wrapped in `<details>` — never expanded by default (CORE-049 noise reduction).

### BLOCK-PHASE-ROADMAP

Rendered once at the start of any multi-phase operation (N≥2 phases), giving users the full journey before work begins. Updates when phases complete.

**SSOT:** `.github/templates/cortex-response-templates.md` §BLOCK-ENGAGEMENT-BREADCRUMB, §BLOCK-ENGAGEMENT-TIMELINE, §BLOCK-PHASE-ROADMAP.

*Verified against orchestrator engagement standards*
