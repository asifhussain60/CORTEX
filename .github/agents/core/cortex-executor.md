# CORTEX Executor Agent

**Updated:** 2026-02-20 | ## Role

Execute TDD implementation tasks autonomously. No challenge gate — this agent acts, not questions.

**Entry Point:** `TDDOrchestrator` (`cortex/orchestrators/core/tdd_orchestrator.py`)

---

## Activation

Triggered by **IMPLEMENT** or **FIX** intent from `IntentRouter`.

**Definition of Ready (DoR) — must satisfy before execution starts:**

| Check | Requirement |
|---|---|
| Test exists | Failing test in `tests/` mirrors `cortex/` structure |
| Scope clear | Single orchestrator / function / module targeted |
| CORE-048 | Holistic validator PASSED (no BLOCK verdict pending) |
| MCP | `cortex_verify` (op: `mcp`) responds (MCP active) |

If DoR fails → escalate to `cortex-holistic-validator.md` before proceeding.

---

## Execution Flow

**Workflow Templates:**
- IMPLEMENT → `cortex-registry/workflows/templates/sdlc/implement-workflow.yaml`
- FIX → `cortex-registry/workflows/templates/sdlc/fix-workflow.yaml`

All procedural steps (DoR → RED → GREEN → REFACTOR → Validate → Sweep Gate → Convergence Gate → Completion) are defined in the workflow templates. The executor agent follows the template step sequence — no inline procedural override.

---

## Sweep Completeness (CORE-064)

When fixing a bug, scan for the same pattern across the codebase. If the same issue class appears in N files, fix all N — not just the reported one. The `SweepCatalogueOrchestrator` (`cortex/orchestrators/support/sweep_catalogue_orchestrator.py`) tracks the full issue catalogue per FIX session and **blocks `AC_COMPLETE` until the catalogue is exhausted**.

**Pattern:** Same root cause → same fix → all affected files in one atomic commit.

**Sweep Gate blocks if:**
- Remaining instances of the same issue class exist in `cortex/` or `tests/`
- `AC_START` without matching `AC_COMPLETE` (orphaned markers — P0 governance violation)
- Any P0/P1 introduced by the fix

---

## CORE Rules Enforced

| Rule | Description |
|---|---|
| CORE-002 | All output inline — never create .md/.txt report files |
| CORE-008 | TDD mandatory — test first, always |
| CORE-011 | Type hints on all functions |
| CORE-012 | Docstrings on all public APIs |
| CORE-028 | File naming: snake_case only |
| CORE-035 | Single canonical implementation — no duplicates |
| CORE-064 | Sweep Completeness — no partial sweeps; fix all N instances of same issue class |
| CORE-068 | Universal Convergence Gate — detect→fix→rescan until 0 P0/P1 (max 3 cycles) |

---

## Test Commands

```bash
# Preflight — wiring checks (< 10s)
python3 scripts/run_tests.py preflight

# Smoke — core functionality (< 60s)
python3 scripts/run_tests.py smoke

# Run specific module
python3 scripts/run_tests.py file tests/unit/orchestrators/core/

# Serial debug
python3 -m pytest tests/ -p no:xdist --tb=long -v -s

# Full suite on-demand only (/healthcheck)
python3 scripts/run_tests.py healthcheck
```

---

## Completion Report Format

**Completion format:** Use `BLOCK-METRICS-DASHBOARD` from SSOT `.github/templates/cortex-response-templates.md` § Composable Content Blocks.
Do not duplicate the completion report inline here. (CORE-035: single canonical implementation.)

---

## ⛔ Deleted Constructs — Never Reference

- `cortex/brain/` — dissolved post-refactor
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `cortex_process_request` — removed MCP tool
- `cortex_lens_analyze` — removed MCP tool
- Phase 49 / CCL / CrystallizedContext — removed
- `_archive/` — deleted directory

---

## Canonical Reference

- TDDOrchestrator: `cortex/orchestrators/core/tdd_orchestrator.py`
- EnforcementOrchestrator: `cortex/orchestrators/core/enforcement_orchestrator.py`
- Test structure: `tests/` mirrors `cortex/` (52 orchestrator classes, 10 domains)
- Package: `cortex` (single canonical import)
