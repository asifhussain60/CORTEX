---
id: governance-convergence-gate-core-068
title: Universal convergence gate (CORE-068)
purpose: Show the detect→fix→rescan loop that guarantees zero P0/P1 violations before any work is marked complete.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml
  - cortex-registry/core/CORE-068.yaml
last_verified: 2026-03-03
diagram_type: Governance
render: ascii
---

# Universal Convergence Gate — CORE-068

## The Core Guarantee: Work Is NEVER Done in One Pass

```
 ═══════════════════════════════════════════════════════════════════════════════
  "Good enough" is not an exit condition. Zero P0/P1 is.
 ═══════════════════════════════════════════════════════════════════════════════

                    Code changes made (IMPLEMENT / FIX / REFACTOR)
                                       │
                                       ▼
                         ┌─────────────────────────┐
                    ┌───▶│      1. DETECT           │
                    │    │                           │
                    │    │  Rescan for:              │
                    │    │  • Test failures          │
                    │    │  • Compliance violations  │
                    │    │  • Regressions from fix   │
                    │    │  • New issues introduced  │
                    │    └────────────┬──────────────┘
                    │                 │
                    │                 ▼
                    │    ┌─────────────────────────┐
                    │    │   P0 or P1 found?       │
                    │    └────────┬───────┬────────┘
                    │             │       │
                    │          YES│       │NO
                    │             │       │
                    │             ▼       ▼
                    │    ┌──────────┐  ┌──────────────────┐
                    │    │ 2. FIX   │  │  ✅ CONVERGED    │
                    │    │          │  │                    │
                    │    │ Remediate│  │  P0 = 0, P1 = 0   │
                    │    │ all P0   │  │  Tests passing     │
                    │    │ and P1   │  │                    │
                    │    │ issues   │  │  → AC_COMPLETE     │
                    │    └────┬─────┘  └──────────────────┘
                    │         │
                    │         ▼
                    │    ┌─────────────────────────┐
                    │    │      3. RESCAN           │
                    │    │                           │
                    │    │  Verify fixes didn't      │
                    │    │  introduce new issues     │
                    │    └────────────┬──────────────┘
                    │                 │
                    │         cycle < max (3)?
                    │             │       │
                    │          YES│       │NO (exhausted)
                    │             │       │
                    └─────────────┘       ▼
                                  ┌──────────────────┐
                                  │  ⛔ ESCALATE     │
                                  │                    │
                                  │  Surface remaining │
                                  │  issues inline     │
                                  │  Block AC_COMPLETE │
                                  │  Require user      │
                                  │  override          │
                                  └──────────────────┘
```

## Convergence Predicates by Mode

```
  ┌───────────┬────────────────────────────────────────────────────┐
  │   Mode    │   Exit Condition (ALL must be true)                │
  ├───────────┼────────────────────────────────────────────────────┤
  │ IMPLEMENT │ test_pass_count ≥ baseline AND lint_errors == 0    │
  │ FIX       │ regression_count == 0 AND original_bug_fixed       │
  │ REFACTOR  │ test_pass_count ≥ baseline AND no_new_lint_errors  │
  │ AUDIT     │ p0_count == 0 AND p1_count == 0                    │
  │ DEBUG     │ no_orphaned_markers AND fix_plan_verified           │
  │ VACUUM    │ no_new_sprawl AND link_check_passed                 │
  └───────────┴────────────────────────────────────────────────────┘
```

**Business impact:** Quality is mathematically guaranteed, not aspirational. The loop runs until the predicate is satisfied or escalates — there is no "ship it anyway" path without explicit human override.
