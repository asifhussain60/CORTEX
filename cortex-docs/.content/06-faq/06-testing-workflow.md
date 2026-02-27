# FAQ — Testing & Development Workflow

---
title: FAQ — Testing & Development Workflow
type: reference
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/testing/ + pytest.ini + conftest.py + scripts/run_tests.py
order: 6
---

> **Purpose:** Answers to questions about the CORTEX test suite, how to run tests correctly, how to write new tests, and day-to-day development workflow patterns. All answers verified against `pytest.ini`, `conftest.py`, and `scripts/run_tests.py`.

---

## What test runner does CORTEX use?

**pytest-xdist** with the `CortexXdistPlugin` batch reporter — configured via `pytest.ini`:

```ini
addopts = -n auto --dist loadscope
```

The `CortexXdistPlugin` (registered in `conftest.py`) provides:
- Live batch boundaries (batches of 500 tests)
- Pass/fail counts per batch
- Final summary table with timing

**CORTEX_BATCH_SIZE=500** controls batch size (default 500, configurable via env var).

---

## How do I run the test suite correctly?

**Always use the canonical runner:**

| Command | What It Runs |
|---------|-------------|
| `make test-batch` | Full batch run — canonical, recommended |
| `make test-smoke` | `@pytest.mark.smoke` tests only (~30s) |
| `make test-fast` | Unit tests only |
| `make test-all` | Everything (no ignore patterns) |
| `python3 scripts/run_tests.py batch` | Cross-platform equivalent of `make test-batch` |
| `python3 scripts/run_tests.py smoke` | Cross-platform smoke tests |

**Never use these:**

| Forbidden Pattern | Why |
|------------------|-----|
| `python3 -m pytest tests/ -x -q` | `-q` silences the batch reporter |
| `pytest -o addopts=` | Wipes xdist config entirely |
| `pytest -x` alone | Stops before batch summary |
| `.venv/bin/python -m pytest` | Hard-codes Unix venv path — breaks on Windows |

---

## How many tests does CORTEX have?

The test suite is comprehensive, spanning multiple categories:

| Category | Location |
|----------|---------|
| Golden | `tests/golden/` (deterministic, serial) |
| Phase | `tests/` (phase-specific) |
| Unit | `tests/unit/` |
| Integration | `tests/integration/` |

Golden tests run serially (no xdist) for deterministic results. They must always pass — CORE-055.

---

## What is the TDD workflow I must follow?

**CORE-008: TDD Mandatory.** For every IMPLEMENT or FIX:

```
1. RED   → Write a failing test in tests/ that specifies the behaviour
2. GREEN → Write the minimum code in cortex/ to make the test pass
3. REFACTOR → Clean up code while keeping all tests green
```

**Practical rules:**
- Tests live in `tests/` — mirroring the `cortex/` structure (`tests/unit/orchestrators/` mirrors `cortex/orchestrators/`)
- Test files are named `test_{module_name}.py` (CORE-026)
- Test functions are named `test_{what_it_tests}_{expected_outcome}` (CORE-026)
- Tests must import from `cortex.*` only — never from relative paths

---

## Where should I put my tests?

Mirror the `cortex/` source structure under `tests/`:

| Source Module | Test Location |
|---------------|--------------|
| `cortex/orchestrators/core/tdd_orchestrator.py` | `tests/unit/orchestrators/test_tdd_orchestrator.py` |
| `cortex/lens/analyzers/ast_analyzer.py` | `tests/unit/lens/test_ast_analyzer.py` |
| `cortex/mcp/tools/core.py` | `tests/mcp/test_core_tools.py` |
| `cortex/infrastructure/audit_db.py` | `tests/unit/infrastructure/test_audit_db.py` |

**Integration tests** (`tests/integration/`) test cross-component workflows.
**Golden tests** (`tests/golden/`) test canonical contracts that must never regress.

---

## What markers does CORTEX use?

| Marker | Used For | How To Run |
|--------|---------|-----------|
| `@pytest.mark.smoke` | Critical path tests — run in < 30s | `make test-smoke` |
| `@pytest.mark.unit` | Isolated unit tests | `make test-fast` |
| `@pytest.mark.integration` | Cross-component tests | `python3 scripts/run_tests.py integration` |
| `@pytest.mark.golden` | Golden tier — always pass | `python3 scripts/run_tests.py golden` |
| `@pytest.mark.phase` | Phase completion tests | Included in `batch` |

---

## What is a golden test and how do I write one?

Golden tests validate **immutable contracts** — behaviours that must never change:

```python
# tests/golden/test_intent_router_golden.py
import pytest
from cortex.orchestrators.core.intent_router import IntentRouter

@pytest.mark.golden
def test_implement_intent_routes_to_tdd():
    """GOLDEN: IMPLEMENT intent must always route to TDDOrchestrator."""
    router = IntentRouter()
    result = router.detect_intent({"request": "implement user authentication"})
    assert result.intent_type == "IMPLEMENT"
    assert result.confidence >= 0.7
```

Golden tests are **strict** — no mocks, no stubs, real implementations only. They document the canonical behaviour of the system.

---

## How do I use `validate_orchestrator_context` in MCP tools?

All MCP tool functions that call `validate_orchestrator_context(orchestrator_context)` must guard the call:

```python
def my_mcp_tool(request: str, orchestrator_context=None):
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)
    # ... tool logic
```

**Why:** The guard allows direct test invocation without a `MasterOrchestrator` context (the `orchestrator_context` is `None` in tests), while still enforcing routing validation in production (where context is always supplied).

Without the guard, tests calling the tool directly will raise a validation error.

---

## How do I debug a failing test?

Use the Debug task (verbose, no xdist):
```bash
# Via VS Code task:
# "CORTEX: Debug (verbose + stdout)"

# Or directly:
python3 -m pytest tests/path/to/test_file.py -p no:xdist --tb=long -v -s
```

`-p no:xdist` disables parallelism so you get sequential output.
`--tb=long` shows full tracebacks.
`-s` captures stdout (print statements appear).

---

## What is `conftest_optimize.py`?

`tests/conftest_optimize.py` contains pytest performance optimizations:
- Session-scoped fixtures that are expensive to create (e.g. LENS orchestrator instances)
- Shared mock registries
- xdist worker configuration

It runs after the main `tests/conftest.py`. Do not put fixtures in `conftest_optimize.py` that need to be available at collection time — those belong in `tests/conftest.py`.

---

## How do I write a test for a new MCP tool?

```python
# tests/mcp/test_my_new_tool.py
import pytest
from cortex.mcp.tools.my_module import my_new_tool

@pytest.mark.unit
def test_my_new_tool_returns_expected_structure():
    """Unit test: no orchestrator_context needed for direct invocation."""
    result = my_new_tool(request="test input", orchestrator_context=None)
    assert result is not None
    assert "status" in result

@pytest.mark.integration  
def test_my_new_tool_with_real_orchestrator():
    """Integration test: full stack, real orchestrator context."""
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    master = MasterOrchestrator()
    ctx = master.create_context()
    result = my_new_tool(request="test input", orchestrator_context=ctx)
    assert result["status"] == "success"
```

---

## What is the TestQualityGate score I should aim for?

**≥ 7** for any test you intend to keep long-term. The scoring criteria:

| Score | Classification | Action |
|-------|---------------|--------|
| 7–9 | KEEP — golden tier candidate | Submit as-is |
| 4–6 | REVIEW — marginal value | Improve or remove |
| 0–3 | DELETE — consuming CI time | Remove |

Score your test with `cortex_generate_tests` (MCP tool) — it returns the TestQualityGate score alongside the generated scaffold.

---

## What happens during `make test-batch`?

1. `CortexXdistPlugin` is activated via `conftest.py` plugin registration
2. pytest collects all tests (respecting `pytest.ini` ignore patterns)
3. Tests are distributed across `n auto` workers (one per CPU core) with `loadscope` distribution
4. Tests run in batches of 500 with live progress output
5. `CortexXdistPlugin` writes the final summary table (pass/fail counts, timing per batch)
6. Exit code: `0` if all pass, `1` if any fail

**Why `--dist loadscope`:** Tests in the same module run on the same worker — this avoids database contention when multiple tests write to `.cortex-runtime/audit.db`.

---

## What are golden tests and how do they differ from regular tests?

Golden tests are the 486 tests in `tests/golden/` governed by **CORE-055**. They represent verified truth about CORTEX behaviour and must ALWAYS pass — zero exceptions. Key differences:

| Aspect | Regular Tests | Golden Tests |
|--------|---------------|--------------|
| **Location** | `tests/unit/`, `tests/integration/` | `tests/golden/` |
| **Governance** | Normal test coverage | CORE-055 — zero regression |
| **Quality Score** | Not scored | Scored 0–9 by `TestQualityGate` |
| **Promotion** | N/A | Must score ≥ 7, ≥ 2 orchestrator refs, ≥ 2 asserts |
| **CI Impact** | Test failure = warning | Test failure = pipeline STOP |

See: `flat-files/14-golden-tests.md` for full documentation.

---

## What is the RGR (Red-Green-Refactor) cycle in CORTEX?

CORTEX implements a **two-level RGR** cycle:

**Level 1 (Unit RGR):** For each feature/fix — `TDDOrchestrator` enforces RED (failing test) → GREEN (minimum implementation) → REFACTOR (clean up). Mandatory per CORE-008.

**Level 2 (Sweep RGR):** For codebase-wide quality — `SweepCatalogueOrchestrator` runs DETECT → FIX → RESCAN loops until all P0/P1 issues are resolved (CORE-064). Each individual fix within the sweep follows Level 1 RGR.

See: `flat-files/18-rgr-quality-cycle.md` for full documentation.

---

## What is STS (Sharpen The Saw)?

STS is the demo repository ecosystem at `cortex-sts/CortexLabs/` used to showcase CORTEX capabilities. It contains:

- **`BadMonolith/`** — Intentionally problematic C#/.NET monolith (0 tests, god classes, no DI)
- **`Refactored/`** — The result after CORTEX transformation

Three usage scenarios: (1) onboarding demos with `/onboard`, (2) digest comparison with `/digest`, (3) live refactoring workshops. CORE rules are exempted from STS code since it's intentionally bad for demonstration.

See: `flat-files/15-sharpen-the-saw.md` for full documentation.

---

*Verified against `pytest.ini` + `conftest.py` + `scripts/run_tests.py`*
