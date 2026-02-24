# Golden Test Taxonomy

**Updated:** 2026-02-24 (Phase 63 — SWEEP-63-GOLDEN-RENAISSANCE)

## Overview

CORTEX golden tests are organized into **canonical subfolders** under `tests/golden/`.
Each subfolder corresponds to a domain and is collected by pytest-xdist for parallel
execution scoped by domain.

## Canonical Subfolder Structure

```
tests/golden/
├── architecture/         ← Intelligence tier structure, memory tier, OrchestratorMixin health
├── audit_trail/          ← AC_START/AC_COMPLETE marker completeness verification
├── governance/           ← CORE rule enforcement, stale construct absence, template governance
├── integration/          ← E2E routing, MCP tool calls, LENS pipeline, CIG pipeline
├── registry/             ← YAML audit: intelligence package, registry correctness
├── synthesis/            ← Knowledge synthesis, canonical import paths, domain brain
├── workflow/             ← Workflow template E2E, trace chains, response rendering
├── holistic_integration/ ← Full S01–S25 scenario suite (Tier 3 complexity)
├── orchestrators/        ← Per-orchestrator truth tests
├── production/           ← Production readiness checks
├── routing/              ← Intent routing differentiation tests
├── onboarding/           ← Repository onboarding E2E tests
├── knowledge_graph/      ← KG indexing and inference truth tests
├── agents/               ← Agent-level golden verifications
└── regression/           ← Regression baselines
```

## Naming Convention

All golden test files follow `test_<domain>_<concern>_truth.py` or `test_<concern>_golden.py`.
Snake_case only (CORE-028).

## Scoring

Golden tests are scored by `cortex/testing/quality_gate.py` using
`cortex-registry/core/test-quality-gate.yaml` (version 2.0 — Phase 63-C).

**Scoring dimensions (version 2.0):**
- **Impact (0–5):** security, reliability, business invariant, workflow template consumption,
  response template rendering
- **Likelihood (0–3):** orchestration density, integration seam coverage, scenario YAML driven
- **Detection (0–3):** data correctness, operational observability, trace chain verification
- **Efficiency (0–2):** lines per test, asserts per test
- **Maintenance Penalty (0–-2):** mock ratio, stub ratio, trivial assert ratio

**KEEP threshold:** ≥ 7 | **REVIEW:** 4–6 | **DELETE:** < 4

## Promotion Pipeline

New tests are promoted to GOLDEN tier by `TestClassifierOrchestrator` (CORE-055):
- Must match `tests/golden/` path pattern
- Must score ≥ 7 on quality gate
- Must have ≥ 2 orchestrator references
- Must have ≥ 2 asserts per test function

See: `cortex-registry/workflows/templates/governance/golden-test-promotion.yaml`
