---
title: Red-Green-Refactor (RGR) — The Looped Quality Cycle
type: explanation
audience: [Software Developers, Product Owners, Business Leaders]
last_verified: 2026-02-28
source_of_truth: cortex/orchestrators/core/tdd_orchestrator.py + cortex/orchestrators/support/sweep_catalogue_orchestrator.py + cortex-registry/workflows/templates/tdd/
order: 18
---

# Red-Green-Refactor (RGR) — The Looped Quality Cycle

> **RGR is not a suggestion in CORTEX — it is infrastructure.** CORE-008 makes TDD mandatory for every IMPLEMENT and FIX operation. The TDDOrchestrator enforces the RED → GREEN → REFACTOR cycle automatically, and the SweepCatalogueOrchestrator ensures the cycle repeats until every issue is resolved.

---

## The Core Principle

Most development tools treat testing as an afterthought — something you do _after_ writing code. CORTEX inverts this:

1. **RED** — Write a failing test that specifies the desired behaviour. If the test passes immediately, it's testing nothing useful.
2. **GREEN** — Write the minimum code to make the test pass. No more. No less.
3. **REFACTOR** — Improve the code while keeping all tests green. Extract methods, rename variables, reduce complexity.

This cycle is not run once. It **loops** — once per unit of work, and then again at the sweep level to ensure completeness.

---

## Two Levels of RGR

CORTEX implements RGR at two distinct levels:

### Level 1 — Unit RGR (Per Feature/Fix)

The `TDDOrchestrator` at `cortex/orchestrators/core/tdd_orchestrator.py` enforces a single RGR cycle for each atomic change:

```
User: "Add password reset endpoint"
  ↓
RED:      Write test_password_reset_sends_email()
          → Verify it FAILS (no implementation exists)
  ↓
GREEN:    Implement PasswordResetService.reset()
          → Verify test PASSES with minimum code
  ↓
REFACTOR: Extract email template, add error handling
          → Verify ALL tests still PASS
  ↓
VALIDATE: Governance gate + audit trail
```

The TDDOrchestrator blocks progress if:
- No test is written before implementation (CORE-008 violation)
- The test passes before implementation (test is vacuous)
- Tests fail after refactoring (regression introduced)

### Level 2 — Sweep RGR (Across Codebase)

The `SweepCatalogueOrchestrator` at `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` implements CORE-064 — the Sweep Completeness Contract:

```
/audit fix detects: "Weak hashing in auth_service.py"
  ↓
CATALOGUE:  Scan entire codebase for ALL instances of weak hashing
            → Found: auth_service.py, user_service.py, legacy_utils.py
  ↓
SWEEP RGR:  For EACH instance:
            RED:      Write test for secure hashing
            GREEN:    Replace weak hash with bcrypt
            REFACTOR: Extract shared hashing utility
  ↓
VERIFY:     Rescan codebase — are there ZERO remaining instances?
            → YES: Sweep complete, catalogue closed
            → NO:  Loop back to CATALOGUE
```

This ensures no partial sweeps. If you fix one instance of a problem, CORTEX finds and fixes _all_ instances.

---

## The Complete RGR Flow

```
USER REQUEST
    │
    ▼
┌─────────────────────────────────────────────┐
│  STAGE 0: Governance Pre-Flight             │
│  • CORE-008 TDD check                       │
│  • CORE-048 Holistic validation             │
│  • CORE-064 Sweep completeness active       │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  LEVEL 1: Unit RGR                          │
│  ┌─────┐    ┌───────┐    ┌──────────┐      │
│  │ RED │───▶│ GREEN │───▶│ REFACTOR │──┐   │
│  └─────┘    └───────┘    └──────────┘  │   │
│       ▲                                │   │
│       └────────────────────────────────┘   │
│       (loop per unit of work)              │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  LEVEL 2: Sweep RGR (CORE-064)             │
│  ┌───────────┐  ┌─────┐  ┌────────┐       │
│  │ CATALOGUE │─▶│ FIX │─▶│ RESCAN │──┐    │
│  └───────────┘  └─────┘  └────────┘  │    │
│       ▲                               │    │
│       └───────────────────────────────┘    │
│       (loop until 0 P0/P1 remaining)       │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  VALIDATION                                 │
│  • All tests pass (golden + unit + phase)   │
│  • Governance gate: 0 P0 violations         │
│  • Audit trail recorded to SQLite           │
│  • URS reinforcement signal emitted         │
└─────────────────────────────────────────────┘
```

---

## Test Quality Integration

Not all tests are created equal. The `TestQualityGate` at `cortex/testing/quality_gate.py` scores every test generated during RGR:

| Score | Verdict | Action |
|-------|---------|--------|
| ≥ 7 | **KEEP** | Test retained, eligible for golden promotion |
| 4–6 | **REVIEW** | Test needs improvement — may be refactored |
| < 4 | **DELETE** | Test provides insufficient value — removed |

This prevents test bloat. RGR generates _meaningful_ tests, not just coverage-padding stubs.

---

## Reinforcement Signals

Every RGR cycle completion feeds the Unified Reinforcement Signal (URS):

| Outcome | Signal | Confidence Delta |
|---------|--------|-----------------|
| GREEN on first try | STRONG_REWARD | +1.0 |
| GREEN with 1–2 retries | MILD_REWARD | +0.5 |
| Stuck in RED (3+ retries) | MILD_PUNISHMENT | −0.5 |
| Sweep completed (all instances fixed) | STRONG_REWARD | +1.0 |
| Sweep incomplete (session ended early) | STRONG_PUNISHMENT | −1.0 |

Over time, patterns that consistently produce first-try GREEN cycles are promoted to T1 knowledge (confidence ≥ 0.9). Patterns that consistently fail are quarantined (confidence ≤ 0.3).

---

## TDD Workflow Templates

The `cortex-registry/workflows/templates/tdd/` directory provides reusable TDD patterns:

| Template | Purpose |
|----------|---------|
| `tdd-feature-implementation.yaml` | Standard feature implementation with RGR |
| `tdd-api-service.yaml` | API service TDD with contract testing |
| `tdd-frontend-visual.yaml` | Frontend visual component TDD |
| `frontend-tdd-workflow.yaml` | Frontend-specific TDD workflow |
| `test-strategy-matrix.yaml` | Test strategy selection matrix |

Each template includes knowledge context injection from `cortex-registry/knowledge/testing-validation/tdd-best-practices.yaml`.

---

## Why This Matters

For **business leaders**: Every line of code is tested before it's written. Every issue is fixed everywhere, not just in the first place it's found. This means fewer production incidents, lower technical debt, and predictable delivery.

For **product owners**: Sprint velocity increases because RGR catches issues early — when they're cheap to fix. The sweep completeness contract means "done" actually means done.

For **developers**: The RGR cycle is automated. You don't have to remember to write tests first — CORTEX enforces it. You don't have to hunt for other instances of a bug — the sweep catalogue finds them all.
