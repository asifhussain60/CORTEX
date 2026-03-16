---
applyTo: "cortex-registry/workflows/**/*.yaml"
---

# CORTEX Workflow Template Rules

**These rules apply when editing workflow templates.**

## 3-Tier Hierarchy
- **Tier 1 Primitives** (`primitives/`): Atomic reusable steps — gates, loops, markers
- **Tier 2 Mode Workflows** (`{category}/`): One per execution mode (IMPLEMENT, FIX, REFACTOR, etc.)
- **Tier 3 Composites** (`composites/`): Multi-mode compositions (audit-fix, totalrecall)

## Mandatory Primitives (all code-modifying workflows)
Every workflow for IMPLEMENT, FIX, REFACTOR, AUDIT MUST inject:
- `primitives/execution/ac-marker-emit.yaml` — AC_START / AC_COMPLETE markers
- `primitives/execution/git-checkpoint.yaml` — rollback point before changes
- `primitives/governance/holistic-validation-gate.yaml` — CORE-048 pre-gate
- `primitives/governance/sweep-catalogue-open.yaml` / `sweep-catalogue-close.yaml` — CORE-064
- `primitives/validation/detect-fix-rescan-loop.yaml` — CORE-068 convergence (max 3 cycles)

## Convergence Predicates
- IMPLEMENT: `test_pass_count >= baseline AND lint_errors == 0`
- FIX: `regression_count == 0 AND original_bug_fixed`
- REFACTOR: `test_pass_count >= baseline AND no_new_lint_errors`
- AUDIT: `p0_count == 0 AND p1_count == 0`

## Template Structure
- `id:` — unique template identifier
- `name:` — human-readable name
- `mode:` — execution mode (IMPLEMENT, FIX, etc.)
- `steps:` — ordered list of execution steps
- `convergence:` — optional convergence configuration
- `primitives:` — list of injected primitive references

## V2 Conventions
- Route mode detail to skills and keep workflow templates focused on execution primitives
- Keep code-modifying workflows explicitly wired to holistic + sweep + convergence primitives
