# CI/CD Pipeline

---
title: CI/CD — Continuous Integration & Delivery
type: reference
audience: [Software Developers, Product Owners]
last_verified: 2026-02-20
source_of_truth: cortex/infrastructure/ci_cd/ + .github/
order: 4
---

> **Brain analogy:** CI/CD is the **daily health routine** — the brain runs diagnostic scans (tests), checks immune function (governance), and validates neural pathways (integration tests) every single day, whether you feel sick or not.

---

## Pipeline Stages

```
[Push to Branch]
       │
       ▼
[Stage 1: Lint & Type Check]
       │ CORE-011: Type hints
       │ CORE-028: File naming (snake_case)
       │
       ▼
[Stage 2: Unit Tests (Parallel)]
       │ pytest -n auto --dist loadscope
       │ 15,333 tests across all tiers
       │
       ▼
[Stage 3: Golden Tests (Serial)]
       │ 486 golden tests — must ALWAYS pass
       │ pytest -p no:xdist (deterministic)
       │
       ▼
[Stage 4: Governance Validation]
       │ 17 active CORE rules enforced
       │ EnforcementOrchestrator validates
       │
       ▼
[Stage 5: Integration Tests]
       │ pytest -n 4 --dist loadfile
       │ Cross-orchestrator flows
       │
       ▼
[Stage 6: Security Scan]
       │ CORE-035 analyzer
       │ Secret detection, import validation
       │
       ▼
[Merge to Main → Deploy]
```

---

## CI/CD Modules

### `cortex/infrastructure/ci_cd/`

| Module | Purpose |
|--------|---------|
| `core_035_analyzer.py` | Analyze codebase for CORE-035 violations (duplicate implementations) |
| `enforce_core_035.py` | Enforce single canonical implementation rule |
| `production_release.py` | Production release validation and gating |

### Pre-Commit Validation

| Module | Location |
|--------|----------|
| `pre_commit_validator.py` | `cortex/infrastructure/` |
| Pre-commit hooks | `deployment/hooks/` |
| Governance scripts | `scripts/governance/` |

---

## Test Tiers in CI

| Tier | Tests | Execution | Purpose |
|------|-------|-----------|---------|
| Smoke | Subset | Parallel (`-n auto`) | Quick validation |
| Unit | ~15,000 | Parallel (`-n auto --dist loadscope`) | Module-level correctness |
| Golden | 486 | Serial (`-p no:xdist`) | Regression-proof specifications |
| Phase | 177 | Serial | Phase milestone verification |
| Integration | Varies | Parallel (`-n 4 --dist loadfile`) | Cross-component flows |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CORTEX_BATCH_SIZE` | 500 | Test batch size for parallel execution |
| `CORTEX_TEST_TIMEOUT` | 60 | Per-test timeout in seconds |

---

## Governance Gates

CI enforces these gates before merge:

| Gate | Rule | Action on Failure |
|------|------|-------------------|
| Type hints | CORE-011 | Block merge |
| Docstrings | CORE-012 | Block merge |
| File naming | CORE-028 | Block merge |
| No duplicates | CORE-035 | Block merge |
| TDD compliance | CORE-008 | Block merge |
| Holistic validation | CORE-048 | Block merge |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run-tests.sh` | Shell script for running test suites |
| `scripts/validate-production.py` | Production readiness validation |
| `scripts/validate_governance_alignment.py` | Governance alignment check |
| `scripts/enforce-test-naming.py` | Test file naming convention enforcement |
| `Makefile` | Build automation targets |

---

## Practical Examples

**Business Leader:** "Every code change goes through 6 automated validation stages before it can merge. 486 golden tests guarantee no regression. Governance rules are enforced by machines, not people."

**Product Owner:** "CI runs in minutes with parallel test execution. Golden tests run serially for deterministic results. The pipeline blocks any change that violates CORE rules."

**Developer:** "I push a branch and CI validates everything — type hints, tests, governance, security. If golden tests break, the merge is blocked. I fix the issue, push again, and CI re-validates."

---

*Verified against `cortex/infrastructure/ci_cd/` and CI pipeline configuration · 20 February 2026*
