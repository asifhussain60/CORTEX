# Master Orchestrator

---
title: MasterOrchestrator — Executive Coordinator
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-18
source_of_truth: cortex/orchestrators/core/master_orchestrator.py + cortex/__wiring_contract__.yaml
format: diátaxis-explanation
voice: third-person-blended
phase: Production (v8.1, Priority 10)
order: 2
---

> **Role:** The MasterOrchestrator is the entry point for every CORTEX operation. It receives a classified request from the IntentRouter and delegates to the appropriate specialist orchestrator, applying the 4-stage pipeline: Interaction → Intent → Intelligence → Execution.

---

## Responsibility

The MasterOrchestrator does **not** implement features itself. Its role is coordination:

1. **Receive** — Accept the enriched, classified request from the IntentRouter
2. **Validate** — Run the Holistic Validation Gate (CORE-048) before any execution
3. **Delegate** — Route to the correct specialist orchestrator (TDD, Refactoring, Planning, etc.)
4. **Supervise** — Monitor execution and surface errors or governance violations
5. **Report** — Return the inline completion summary to the interaction layer

---

## Position in the Orchestrator Hierarchy

```
MasterOrchestrator  (Priority 10 — highest)
│
├── IntentRouter           (Priority 20)  → classifies requests
├── InteractionOrchestrator (Priority 30) → formats responses
├── LENSSynthesis          (Priority 40)  → code intelligence
├── EnforcementOrchestrator (Priority 50) → governance gate
├── TDDOrchestrator        (Priority 55)  → IMPLEMENT/FIX
├── RefactoringOrchestrator (Priority 60) → REFACTOR
├── IncrementalTaskDecomposer (Priority 70) → large task chunking
├── PlanningOrchestrator   (Priority 75)  → PLAN/DESIGN
├── WorkflowOrchestrator   (Priority 80)  → multi-step sequences
└── ... (domain + support + infrastructure)
```

Priority numbers determine execution order within concurrent operations, not importance ranking.

---

## 4-Stage Pipeline

Every request flows through four stages regardless of intent type:

### Stage 1 — Interaction
- Parse raw request from MCP tool call
- Apply Stage -1 pre-processing via `RequestRephraseOrchestrator`
- Load user context (session state, recent history)
- Determine response format (silent, educational, verification)

### Stage 2 — Intent
- Pass enriched request to `IntentRouter`
- Receive classification: intent type + confidence + target orchestrator
- Load governance context (CORE rules relevant to this intent)
- If Tier 0 intent (IMPLEMENT/FIX/REFACTOR/AUDIT): proceed to validation gate

### Stage 3 — Intelligence
- Trigger `LENSSynthesis` for codebase analysis (async, pre-warmed when possible)
- Retrieve knowledge base patterns relevant to the request domain
- Build execution context: dependency graph, risk score, architecture snapshot

### Stage 4 — Execution
- Invoke target orchestrator with enriched context
- Monitor for governance violations during execution
- Collect audit markers (AC_START / AC_COMPLETE)
- Return result to InteractionOrchestrator for formatting

---

## Holistic Validation Gate

Before any Tier 0 operation proceeds to execution, the gate runs 7 checks:

| Check | Tool | Verdict Threshold |
|-------|------|-------------------|
| Registry consistency | `cortex_query_governance` | PASS / FAIL |
| Context pre-warming | `LENSSynthesis` async | Ready / Timeout |
| Dependency graph | `UnifiedAnalysisOrchestrator` | Risk 0.0–1.0 |
| Regression risk score | Internal scorer | <0.4 PASS, 0.4–0.7 WARN, >0.7 BLOCK |
| Architecture drift | `SOLIDOrchestrator` | Drift % |
| Challenge gate | `UnifiedQualityAssuranceOrchestrator` | Alternatives presented |
| CORTEX self-analysis | Brain tier | Confidence score |

**Output:** PASS → proceed. WARN → present to user. BLOCK → reject with explanation.

---

## Error Handling

The MasterOrchestrator implements circuit-breaker logic for all delegated orchestrators:

```
Orchestrator call fails
        │
        ▼
Retry (max 2 attempts, 500ms backoff)
        │
        ├─ Success → continue
        │
        └─ Failure → fallback:
               ├─ Degraded mode (partial result)
               └─ Hard stop (governance violation)
```

All failures are logged to `cortex_intelligence/governance.db` with full context.

---

## Key Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Delegation latency | <5ms | MasterOrchestrator overhead only |
| Validation gate | ~150ms | 7-step parallel where possible |
| End-to-end (simple) | <2s | Including LENS warm path |
| End-to-end (complex) | <5.5s | Multi-step TDD on large files |

---

## Related Documents

- **[Orchestration Overview](./01-overview.md)** — Full orchestrator registry
- **[Intent Router](./03-intent-router.md)** — How requests are classified
- **[TDD Orchestrator](./04-tdd-orchestrator.md)** — Primary implementation engine
- **[Holistic Validation Gate](../01-capabilities/07-governance-compliance.md)** — Gate detail

---

*Last verified: 2026-02-18 | Source: cortex/orchestrators/core/master_orchestrator.py*
