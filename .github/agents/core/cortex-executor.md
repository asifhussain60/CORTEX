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

```
DoR Check
    ↓ PASS
RED Phase → write failing test (CORE-008)
    ↓
GREEN Phase → minimum implementation to pass test
    ↓
REFACTOR Phase → clean up, type hints (CORE-011), docstrings (CORE-012)
    ↓
Validate → pytest tests/ -n auto --dist loadscope
    ↓
Completion Report (inline — CORE-002)
```

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

---

## Test Commands

```bash
# Run full suite parallel
python3 -m pytest tests/ -n auto --dist loadscope --tb=short

# Run specific module
python3 -m pytest tests/unit/orchestrators/core/ -n auto --dist loadscope -v

# Serial debug
python3 -m pytest tests/ -p no:xdist --tb=long -v -s
```

---

## Completion Report Format

```
## ✅ Execution Complete

**Task:** [description]
**Phase:** RED → GREEN → REFACTOR
**Tests:** X passed, 0 failed
**Files changed:** [list]
**CORE rules satisfied:** CORE-002, CORE-008, CORE-011, CORE-012
```

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
