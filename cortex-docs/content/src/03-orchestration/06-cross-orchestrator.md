# Cross-Orchestrator Communication

---
title: Cross-Orchestrator Communication — Internal Messaging & State Sharing
type: explanation
audience: [Software Developers, Architects]
last_verified: 2026-02-18
source_of_truth: cortex/wiring/ + cortex/__wiring_contract__.yaml + cortex/orchestrators/core/orchestrator_base_protocol.py
format: diátaxis-explanation
voice: third-person-neutral
phase: Production (v8.1)
order: 6
---

> **Purpose:** Explains how the 21 orchestrators exchange information, share state, and coordinate without tight coupling. New contributors need this to understand how to add orchestrators or modify existing ones without breaking the system.

---

## Design Principle: Loose Coupling via Contracts

Orchestrators do **not** call each other directly. All communication flows through a **wiring contract** — a YAML-defined registry that specifies:

- Which orchestrator handles which intent
- What context each orchestrator expects as input
- What output shape each orchestrator produces
- Which orchestrators may chain in sequence

This means adding a new orchestrator requires only:
1. Implementing the `OrchestratorBaseProtocol`
2. Registering in `cortex/__wiring_contract__.yaml`
3. Writing tests (TDD mandatory)

No other orchestrator's code is touched.

---

## OrchestratorBaseProtocol

All orchestrators implement this interface:

```python
class OrchestratorBaseProtocol:
    """
    Base contract that all CORTEX orchestrators must satisfy.
    Authority: cortex/__wiring_contract__.yaml
    """

    priority: int                    # Execution order (lower = earlier)
    intent_types: list[str]          # Which intents this handles
    required_context: list[str]      # Keys that must be in context dict

    async def execute(
        self,
        request: OrchestratorRequest,
        context: OrchestratorContext,
    ) -> OrchestratorResult:
        """Execute the orchestrator's primary workflow."""
        ...

    async def health_check(self) -> HealthStatus:
        """Return current availability status."""
        ...
```

---

## Context Object

The `OrchestratorContext` travels with every request and accumulates data as it passes through the pipeline:

```
OrchestratorContext
├── request_id          # UUID — links audit trail
├── intent              # Classified intent (IMPLEMENT, FIX, AUDIT, …)
├── user_input          # Original + rephrased request
├── lens_snapshot       # LENS analysis result (may be pre-warmed)
├── governance_rules    # Applicable CORE rules for this intent
├── session_state       # User session (recent history, preferences)
├── risk_score          # 0.0–1.0 from holistic validation gate
├── audit_markers       # AC_START / AC_COMPLETE entries accumulated
└── metadata            # Timestamps, token counts, performance data
```

Each orchestrator **reads** from context, appends its own output to context, and passes it forward. No orchestrator mutates another orchestrator's keys.

---

## Communication Patterns

### Pattern 1 — Sequential Pipeline

The standard request flow: each orchestrator processes and hands off.

```
RequestRephraseOrchestrator
        │ enriched request
        ▼
IntentRouter
        │ classified intent + target
        ▼
MasterOrchestrator
        │ context + LENS snapshot
        ▼
TDDOrchestrator (or other target)
        │ result + audit markers
        ▼
EnforcementOrchestrator
        │ validated result
        ▼
InteractionOrchestrator
        │ formatted response
        ▼
User
```

### Pattern 2 — Parallel Fans

Some orchestrators launch parallel sub-tasks and aggregate results:

```
LENSSynthesis
├── ASTAnalyzer          ─┐
├── GitHistoryAnalyzer    │  (parallel)
├── CommentAnalyzer       │
├── ConfigAnalyzer        ├─► Aggregated intelligence snapshot
├── DependencyAnalyzer    │
├── APIContractAnalyzer   │
├── DatabaseAnalyzer      │
└── PolyglotDetector     ─┘
```

Parallel fans use `asyncio.gather()` with a configurable timeout. Slow analyzers are skipped rather than blocking the pipeline.

### Pattern 3 — Conditional Routing

The IntentRouter applies conditional dispatch:

```
Confidence > 0.85 → direct route to target orchestrator
Confidence 0.60–0.85 → route with clarification prompt
Confidence < 0.60 → ConversationOrchestrator for disambiguation
```

### Pattern 4 — Circuit Breaker

If an orchestrator fails twice within 60 seconds, the circuit opens:

```
Orchestrator failure
        │
        ▼
Retry × 2 (500ms backoff)
        │
        ├── Recovered → reset circuit
        │
        └── Still failing → circuit OPEN
                │
                ├── Degraded mode (skip non-critical)
                └── Hard stop (critical orchestrator failed)
```

Open circuits recover automatically after 30 seconds.

---

## Wiring Contract Structure

`cortex/__wiring_contract__.yaml` is the single source of truth for all orchestrator registration:

```yaml
orchestrators:
  - id: TDDOrchestrator
    priority: 55
    intent_types: [IMPLEMENT, FIX]
    required_context: [lens_snapshot, governance_rules, risk_score]
    produces: [implementation_result, test_results, audit_markers]
    timeout_ms: 5000
    circuit_breaker: true

  - id: PlanningOrchestrator
    priority: 75
    intent_types: [PLAN, DESIGN]
    required_context: [user_input, session_state]
    produces: [phase_plan, dor_checklist, roi_score]
    timeout_ms: 3000
    circuit_breaker: false
```

The `ContractValidator` infrastructure orchestrator (Priority 3) validates this file on every startup and on every `git commit`, blocking deployments if the contract is invalid.

---

## Adding a New Orchestrator

1. **Create** `cortex/orchestrators/{category}/{name}_orchestrator.py`
2. **Implement** `OrchestratorBaseProtocol`
3. **Register** in `cortex/__wiring_contract__.yaml`
4. **Write tests** in `tests/orchestrators/{name}/` (TDD: test first)
5. **Validate**: `python -m cortex.bootstrap --validate-contracts`

The MasterOrchestrator picks up new registrations automatically on next startup.

---

## Related Documents

- **[Orchestration Overview](./01-overview.md)** — Full orchestrator registry
- **[Master Orchestrator](./02-master-orchestrator.md)** — Top-level coordinator
- **[End-to-End Flow](./08-end-to-end-flow.md)** — Full request trace
- **[Extensibility](../01-capabilities/11-extensibility.md)** — Plugin architecture

---

*Last verified: 2026-02-18 | Source: cortex/wiring/ + cortex/__wiring_contract__.yaml*
