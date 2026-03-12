---
name: cortex-tdd
description: 'CORTEX TDD workflow skill. Use when: implementing features, fixing bugs, refactoring code, or any code-modifying operation. Covers CORE-008 TDD cycle (RED-GREEN-REFACTOR), holistic validation gate (CORE-048), sweep completeness (CORE-064), convergence gate (CORE-068), and workflow template routing for IMPLEMENT, FIX, and REFACTOR intents.'
argument-hint: 'implement <feature> | fix <bug> | refactor <scope>'
---

# CORTEX TDD Workflow

**TDD is mandatory for all code-modifying operations (CORE-008).**

---

## TDD Cycle

```
IMPLEMENT / FIX / REFACTOR
  ↓
Holistic Validation Gate (CORE-048)
  ↓
RED: Write failing test FIRST — implementation forbidden
  ↓
GREEN: Minimum implementation to pass test
  ↓
REFACTOR: Type hints, docstrings, dedup (CORE-011, CORE-012, CORE-035)
  ↓
Convergence loop (detect-fix-rescan, max 3 cycles — CORE-068)
  ↓
make test-smoke → must be GREEN
```

---

## Workflow Templates

| Intent | Template | Pre-Gate |
|---|---|---|
| IMPLEMENT | `sdlc/implement-workflow.yaml` | `holistic-validation-gate.yaml` |
| FIX | `sdlc/fix-workflow.yaml` | `holistic-validation-gate.yaml` |
| REFACTOR | `quality/refactor-workflow.yaml` | `holistic-validation-gate.yaml` |

Templates live in `cortex-registry/workflows/templates/`.

---

## IMPLEMENT Mode

**Trigger:** "build", "create", "add", "implement"

Primitives auto-injected:
- `holistic-validation-gate.yaml` (CORE-048)
- `challenge-gate.yaml` (risk >0.4 or scope >3 files)
- `sweep-catalogue-open.yaml` / `sweep-catalogue-close.yaml` (CORE-064)
- `detect-fix-rescan-loop.yaml` (CORE-068, max 3 cycles)
- `ac-marker-emit.yaml` + `git-checkpoint.yaml`

**Convergence predicate:** `test_pass_count >= baseline AND lint_errors == 0`

---

## FIX Mode

**Trigger:** "fix", "bug", "broken", "error", "failing"

Key additions over IMPLEMENT:
- **REPRODUCE** — create failing test demonstrating the bug
- **ROOT CAUSE** — LENS analysis on affected files (AST + git history)
- **SWEEP GATE** (CORE-064) — scan for same pattern across codebase; fix ALL N instances

**Convergence predicate:** `regression_count == 0 AND original_bug_fixed`

---

## REFACTOR Mode

**Trigger:** "refactor", "improve", "optimize", "consolidate"

Key features:
- Functional baseline at step 0 → completeness gate at final step
- Security hardening gate
- Weighted scorecard at completion

| Category | Weight |
|---|---|
| Architecture | 25% |
| Security | 25% |
| Testing | 20% |
| Documentation | 15% |
| Frontend | 10% |
| Traceability | 5% |

**Convergence predicate:** `test_pass_count >= baseline AND no_new_lint_errors`

Refactoring checks: dead code elimination, duplicate consolidation (CORE-035), complexity reduction (functions >50 lines), import cleanup, DI lifetime consistency.

---

## Key Rules

| Rule | What |
|---|---|
| CORE-008 | Write failing test FIRST — no exceptions |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-048 | Holistic validation gate before any code change |
| CORE-064 | Sweep completeness — exhaust the full catalogue |
| CORE-068 | Convergence gate — detect→fix→rescan until 0 P0/P1 |

---

## Test Runner

ALWAYS use `python3 scripts/run_tests.py {mode}` or `make test-{mode}` — never raw `pytest`.

| Mode | Command | When |
|---|---|---|
| changed | `make test-changed` | TDD inner loop |
| smoke | `make test-smoke` | Before commit (< 60s) |
| preflight | `make test-preflight` | Audit gate (< 10s) |

---

## MCP Tool

Execute workflows directly: `cortex_workflow op=execute template_id=sdlc/implement-workflow`
