# TDDOrchestrator

---
title: TDDOrchestrator — Test-Driven Development Engine
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/orchestrators/core/tdd_orchestrator.py
order: 4
---

> **Brain analogy:** TDDOrchestrator is the **motor cortex with a safety interlock**. The motor cortex plans and executes movements, but the cerebellum constantly checks coordination. TDDOrchestrator executes code changes but the TDD cycle (RED→GREEN→REFACTOR) constantly validates correctness.

## The TDD Cycle

```
RED ──────────── Write a failing test that specifies behaviour
  │
  ▼
GREEN ─────────── Write minimum code to make the test pass
  │
  ▼
REFACTOR ──────── Improve code while keeping all tests green
  │
  ▼
VALIDATE ──────── Governance gate + audit trail
```

## CORE-008 Enforcement

CORE-008 mandates TDD for all IMPLEMENT and FIX operations. TDDOrchestrator:

1. Checks that no implementation exists before the test (RED phase)
2. Validates that the test fails initially (confirming it tests something)
3. Guides minimum implementation (GREEN phase)
4. Prompts refactoring with all tests passing (REFACTOR phase)

**Location:** `cortex/orchestrators/core/tdd_orchestrator.py`

**Implements:** `IOrchestrator`

## TestQualityGate Integration

TDDOrchestrator integrates with TestQualityGate (`cortex/testing/quality_gate.py`) to block test generation scoring below 7. Tests must be meaningful, not just present.

## URS Signal Emission

TDDOrchestrator emits **Unified Reinforcement Signals** after every TDD cycle completion, feeding the closed-loop learning system:

| Outcome | Signal | Delta | When |
|---------|--------|-------|------|
| GREEN on first try | `STRONG_REWARD` | +1.0 | Test passes on first implementation attempt |
| GREEN with retries | `MILD_REWARD` | +0.5 | Test passes after ≥1 retry |
| Stuck in RED | `MILD_PUNISHMENT` | −0.5 | Test cannot be made green within cycle budget |

These signals adjust confidence scores on the patterns used during the cycle. Over time, patterns that consistently produce first-try GREEN are promoted to T1 knowledge (confidence ≥0.9), while patterns that consistently fail are quarantined (confidence ≤0.3).

**Location:** `tdd_orchestrator.py → _emit_tdd_cycle_signal()`

---

## Practical Examples

**Business Leader:** "TDD isn't aspirational — it's enforced by the system. Every commit has tests written first."

**Product Owner:** "TDDOrchestrator handles 40% of all requests. Each one produces: (1) a failing test, (2) minimum implementation, (3) refactored code. All three steps are audited."

**Developer:** "I ask CORTEX to implement auth middleware. TDDOrchestrator writes `test_auth_middleware_rejects_unauthenticated()` first (RED). It fails. Then it implements the middleware (GREEN). Then it suggests extracting the token validation into a separate function (REFACTOR)."

---

*Verified against tdd_orchestrator.py*
