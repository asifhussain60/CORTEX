---
title: Golden Tests — Quality Contract and Scoring Engine
type: explanation
audience: [Software Developers, Product Owners]
last_verified: 2026-02-27
source_of_truth: tests/golden/ + cortex/testing/quality_gate.py + cortex-registry/core/test-quality-gate.yaml
order: 14
---

# Golden Tests — Quality Contract and Scoring Engine

> **Golden tests are CORTEX's immune system.** They are the 486 tests that must _always_ pass — across every commit, every CI run, every refactor. If a golden test fails, the operation is blocked. No exceptions. No overrides.

---

## Why Golden Tests Exist

Most test suites grow organically. Tests accumulate, overlap, and eventually some become "flaky" or "ignored." CORTEX inverts this. Golden tests are not accumulated — they are **promoted**. Every golden test earned its position through a scoring gate, and every golden test can be **demoted** if its quality score drops.

The contract is codified as **CORE-055 — Golden Test Tier Contract**: all 486 golden tests must pass with zero regressions. Any failure in `tests/golden/` is a P0 production blocker.

---

## The Golden Test Lifecycle

Golden tests follow a four-stage lifecycle: creation → scoring → promotion → maintenance.

### Stage 1 — Creation (RED Phase)

Every golden test begins as a regular test written during TDD (CORE-008). The developer writes a failing test that specifies a critical behaviour — an orchestrator chain, a governance gate, a LENS pipeline output, or an integration seam.

### Stage 2 — Scoring (Quality Gate)

The `TestQualityGate` at `cortex/testing/quality_gate.py` scores every test using five dimensions defined in `cortex-registry/core/test-quality-gate.yaml` (version 2.0):

| Dimension | Range | What It Measures |
|-----------|-------|-----------------|
| **Impact** | 0–5 | Security, reliability, business invariant, workflow template consumption, response template rendering |
| **Likelihood** | 0–3 | Orchestration density, integration seam coverage, scenario YAML driven |
| **Detection** | 0–3 | Data correctness, operational observability, trace chain verification |
| **Efficiency** | 0–2 | Lines per test, assertions per test — lean tests score higher |
| **Maintenance Penalty** | 0 to −2 | Mock ratio, stub ratio, trivial `assert True` ratio — heavy mocking lowers the score |

**Score = Impact + Likelihood + Detection + Efficiency − Maintenance**

| Score | Verdict |
|-------|---------|
| ≥ 7 | **KEEP** — eligible for golden promotion |
| 4–6 | **REVIEW** — needs improvement before promotion |
| < 4 | **DELETE** — provides insufficient value |

### Stage 3 — Promotion

Tests scoring ≥ 7 are promoted to `tests/golden/` via the golden-test-promotion workflow at `cortex-registry/workflows/templates/governance/golden-test-promotion.yaml`. Promotion involves:

1. Moving the test file to the appropriate golden subfolder
2. Renaming to follow `test_<domain>_<concern>_truth.py` or `test_<concern>_golden.py` convention
3. Registering in the golden test manifest
4. Verifying the test passes in parallel execution (pytest-xdist with `--dist loadscope`)

### Stage 4 — Maintenance

Golden tests are re-scored periodically. If a test's score drops below 7 (due to increased mocking, reduced relevance, or architectural changes), it is demoted back to the regular test suite. This keeps the golden tier lean and meaningful.

---

## Golden Test Architecture

### Canonical Subfolder Structure

```
tests/golden/                          ← 486 golden tests
├── _golden_factory.py                 ← GoldenScenario dataclass + GOLDEN_SCENARIOS registry
├── conftest.py                        ← Golden-specific fixtures
├── architecture/                      ← Intelligence tier structure, OrchestratorMixin health
├── audit_trail/                       ← AC_START/AC_COMPLETE marker verification
├── governance/                        ← CORE rule enforcement, stale construct absence
├── integration/                       ← E2E routing, MCP tool calls, LENS pipeline
├── registry/                          ← YAML audit: intelligence package, registry correctness
├── synthesis/                         ← Knowledge synthesis, canonical import paths
├── workflow/                          ← Workflow template E2E, trace chains, response rendering
├── holistic_integration/              ← Full S01–S25 scenario suite (Tier 3 complexity)
├── orchestrators/                     ← Per-orchestrator truth tests
├── production/                        ← Production readiness checks
├── routing/                           ← Intent routing differentiation tests
├── onboarding/                        ← Repository onboarding E2E tests
├── knowledge_graph/                   ← KG indexing and inference truth tests
├── agents/                            ← Agent-level golden verifications
├── intelligence/                      ← Scorer, unified brain, intelligence matrix
├── mcp/                               ← MCP tool registration and invocation
├── modes/                             ← Execution modes and debug mode
├── phases/                            ← Phase-specific golden tests
└── regression/                        ← Regression baselines
```

### The Golden Scenario Factory

The `GoldenScenario` dataclass at `tests/golden/_golden_factory.py` reduces golden test creation cost by approximately 60% via shared scenario definitions:

```python
@dataclass
class GoldenScenario:
    scenario_id: str                           # e.g., "implement-tdd-cycle"
    intent: str                                # e.g., "implement TDD feature"
    expected_orchestrator_chain: List[str]      # Ordered orchestrators invoked
    acceptance_criteria: List[str]              # Assertions that must pass
    ac_ids: List[str]                           # AC marker IDs to validate
    domain: Optional[str]                       # Domain filter (e.g., "backend-python")
```

Tests parametrize over `GOLDEN_SCENARIOS` to generate comprehensive E2E verification with minimal boilerplate.

---

## Execution

Golden tests run with pytest-xdist parallel execution scoped by domain:

```bash
# Run all golden tests (parallel)
python3 scripts/run_tests.py golden

# Run specific golden domain
python3 -m pytest tests/golden/governance/ -n auto --dist loadscope
```

Golden tests are included in the preflight tier (Stage 9 of `/audit fix`) and the full batch CI gate.

---

## Reinforcement Learning Integration

Golden test outcomes feed the Unified Reinforcement Signal (URS — Phase 83):

| Outcome | Signal | Confidence Delta |
|---------|--------|-----------------|
| All golden tests pass after refactor | STRONG_REWARD | +1.0 |
| Golden test catches a regression | DETECTION_REWARD | +0.8 |
| Golden test becomes flaky | MILD_PUNISHMENT | −0.5 |
| Golden test demoted (score < 7) | NEUTRAL | 0.0 |

This creates a closed-loop: golden tests that consistently catch real regressions get higher confidence scores, while tests that generate false positives are eventually demoted.
