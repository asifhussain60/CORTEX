---
applyTo: "tests/**/*.py"
---

# CORTEX Test Rules

**These rules apply automatically when editing any test file.**

## TDD First (CORE-008)
- Write the failing test BEFORE any implementation — no exceptions
- RED → GREEN → REFACTOR cycle is mandatory
- Every bug fix starts with a test that reproduces the bug

## Test Runner (MANDATORY)
- ALWAYS use `python3 scripts/run_tests.py {mode}` or `make test-{mode}`
- NEVER use raw `pytest`, `python3 -m pytest`, or `.venv/bin/python -m pytest`

| Mode | Command | When |
|---|---|---|
| preflight | `make test-preflight` | Audit gate (< 10s) |
| changed | `make test-changed` | TDD inner loop |
| smoke | `make test-smoke` | Before commit (< 60s) |
| unit | `make test` | Default local dev |
| parallel | `make test-parallel` | Pre-commit full speed |

## Test Naming
- Test files: `test_{module_name}.py` — mirrors `cortex/` structure
- Test classes: `Test{ClassName}`
- Test methods: `test_{behavior_under_test}_{expected_outcome}`
- Mark preflight tests: `@pytest.mark.preflight`

## Test Quality
- Never assert `True` or `assert 1 == 1` — tests must verify real behavior
- Never mock everything — mock only external dependencies
- Every test must have at least one meaningful assertion
- Use `pytest.raises` for expected exceptions, not try/except

## Dissolved Packages
- NEVER create test directories for: `cortex_brain`, `cortex_intelligence`, `cortex_lens`
- These packages were dissolved — their tests live under `tests/` mirroring `cortex/`

## V2 Conventions
- Prefer phase-targeted tests under `tests/v2/` for migration contracts
- Keep smoke/preflight gates as authoritative completion checks for migration phase closure
