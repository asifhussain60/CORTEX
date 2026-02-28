# Universal Convergence Gate (CORE-068)

---
title: Universal Convergence Gate — Detect→Fix→Rescan Until Zero P0/P1
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
last_verified: 2026-02-28
source_of_truth: cortex-registry/core/rules/core-068-convergence-gate.yaml + cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml
order: 14
synced_from: 01-capabilities/14-universal-convergence-gate.md
---

> **The central idea:** No code-modifying operation is ever considered complete in a single pass. CORE-068 mandates a convergence loop — detect problems, fix them, rescan to verify the fix didn't introduce new problems — that repeats until zero P0/P1 issues remain.

---

## Why This Exists

Before CORE-068, CORTEX operations could complete in a single pass even when the fix itself introduced regressions. A developer fixes a bug, the bug fix passes tests, but a new lint error or compliance violation silently enters the codebase. The convergence gate closes this gap by making the detect→fix→rescan loop mandatory for every code-modifying operation.

---

## Which Operations Require Convergence

| Applies to | Exempt |
|---|---|
| IMPLEMENT, FIX, REFACTOR, AUDIT, DEBUG, VACUUM, HEALTH | QUERY, DESIGN, PLAN, DIGEST, REPHRASE, SYNC, TRAIN |

The convergence gate is only mandatory for operations that modify code. Read-only operations skip the gate entirely.

---

## How It Works

```
[Operation completes] → [DETECT: rescan for issues] → [issues found?]
                                                           │
                                            Yes ←──────────┤──────────→ No
                                             │                           │
                                        [FIX issues]               [AC_COMPLETE ✅]
                                             │
                                        [RESCAN]
                                             │
                                        [Loop back to DETECT]
                                        (max 3 cycles)
```

### Convergence Predicate by Mode

Each operation type defines its own convergence predicate — the condition that must be true before the loop exits:

| Mode | Convergence Predicate |
|---|---|
| IMPLEMENT | `test_pass_count >= baseline AND lint_errors == 0` |
| FIX | `regression_count == 0 AND original_bug_fixed` |
| REFACTOR | `test_pass_count >= baseline AND no_new_lint_errors` |
| AUDIT | `p0_count == 0 AND p1_count == 0` |
| DEBUG | `no_orphaned_markers AND fix_plan_verified` |
| VACUUM | `no_new_sprawl AND link_check_passed` |
| HEALTH | `all_endpoints_healthy` |

### Maximum Cycles

The loop runs a maximum of three cycles by default. If issues remain after three cycles, the gate surfaces remaining issues inline, blocks `AC_COMPLETE`, and requires explicit user override.

---

## Governance Rule

**CORE-068** is codified as a governance YAML rule in `cortex-registry/core/rules/` and enforced by the EnforcementOrchestrator at pre-commit. The workflow primitive lives at `cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml`.

---

## Integration with Audit Pipeline

The `/audit fix` pipeline uses the convergence gate in Stages 7–8. These stages loop detect→fix→rescan until `p0_count == 0 AND p1_count == 0`, ensuring the audit pipeline never completes with unresolved P0/P1 violations.

---

*Verified against CORE-068 governance rule, detect-fix-rescan-loop.yaml primitive, and Phase 94 wiring*
