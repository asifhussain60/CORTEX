# Golden Tests & Quality Gate

---
title: Golden Tests — Quality Contract and Scoring
type: capability
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: cortex/testing/quality_gate.py, tests/golden/
order: 11
---

> Golden tests are the highest-tier quality contract in CORTEX. They must ALWAYS pass — zero exceptions.

---

## What Are Golden Tests?

Golden tests are the 486 tests in `tests/golden/` that represent verified truth about CORTEX behaviour. They are governed by **CORE-055 (Golden Test Tier Contract)**: if any golden test fails, the entire CI pipeline stops.

### Key Properties

| Property | Value |
|----------|-------|
| Location | `tests/golden/` (15+ subfolders) |
| Count | 486 tests |
| Governance | CORE-055 — zero regression allowed |
| Execution | `pytest-xdist` parallel (`-n auto --dist loadscope`) |
| Scoring | `TestQualityGate` — 5 dimensions, score 0–9 |

---

## Quality Scoring (v2.0)

Every test is scored by `cortex/testing/quality_gate.py`:

| Dimension | Range | Measures |
|-----------|-------|----------|
| **Impact** | 0–5 | Security, reliability, business invariant coverage |
| **Likelihood** | 0–3 | Orchestration density, integration seam coverage |
| **Detection** | 0–3 | Data correctness, observability, trace verification |
| **Efficiency** | 0–2 | Lines per test, asserts per test |
| **Maintenance** | 0 to −2 | Mock ratio, stub ratio (penalty) |

**Thresholds:** KEEP ≥ 7 · REVIEW 4–6 · DELETE < 4

---

## Promotion Pipeline

Tests are promoted to golden tier by `TestClassifierOrchestrator`:

1. Must be located in `tests/golden/` path
2. Must score ≥ 7 on quality gate
3. Must reference ≥ 2 orchestrators
4. Must have ≥ 2 asserts per test function

---

## GoldenScenario Factory

The `GoldenScenario` dataclass in `cortex/testing/_golden_factory.py` parametrizes E2E test scenarios from YAML fixtures, enabling data-driven golden test generation.

---

**Full documentation:** `flat-files/14-golden-tests.md`
**Diagram:** `07-diagrams/11-golden-test-lifecycle.md`
