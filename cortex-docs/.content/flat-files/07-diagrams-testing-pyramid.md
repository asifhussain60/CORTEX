# Testing Pyramid

---
title: Testing Pyramid & Execution Strategy
type: diagram
audience: [Product Owners, Software Developers]
last_verified: 2026-02-20
source_of_truth: tests/ + pytest.ini + .vscode/tasks.json
order: 8
---

## Test Pyramid

```
                        ▲
                       ╱ ╲
                      ╱   ╲
                     ╱ 177 ╲
                    ╱ Phase  ╲
                   ╱  Tests   ╲
                  ╱─────────────╲
                 ╱               ╲
                ╱    486 Golden   ╲
               ╱     Tests         ╲
              ╱  (must ALWAYS pass) ╲
             ╱───────────────────────╲
            ╱                         ╲
           ╱    Integration Tests      ╲
          ╱    (cross-component)        ╲
         ╱───────────────────────────────╲
        ╱                                 ╲
       ╱       ~15,000 Unit Tests          ╲
      ╱        (module-level)               ╲
     ╱───────────────────────────────────────╲
    ╱                                         ╲
   ╱          Smoke Tests (subset)             ╲
  ╱─────────────────────────────────────────────╲

  Total: 15,739 tests collected
```

## Execution Strategy

```
┌───────────────────────────────────────────────────────────────┐
│                    TEST EXECUTION MODES                       │
├─────────────┬──────────────┬─────────────────────────────────┤
│ Tier        │ Execution    │ Configuration                   │
├─────────────┼──────────────┼─────────────────────────────────┤
│ Smoke       │ Parallel     │ -m smoke -n auto --dist loadfile│
│ Unit        │ Parallel     │ -n auto --dist loadscope        │
│ Integration │ Parallel (4) │ -n 4 --dist loadfile            │
│ Golden      │ Serial       │ -p no:xdist (deterministic)     │
│ Phase       │ Serial       │ -p no:xdist                     │
│ Full Suite  │ Parallel     │ -n auto --dist loadscope        │
│ Debug       │ Serial       │ -p no:xdist --tb=long -v -s     │
└─────────────┴──────────────┴─────────────────────────────────┘
```

## TestQualityGate Scoring

```
Score = Impact + Likelihood + Detection + Efficiency - Maintenance

┌──────────────┬─────────┬────────────────────────────────────┐
│ Factor       │ Range   │ Measures                           │
├──────────────┼─────────┼────────────────────────────────────┤
│ Impact       │ 0-3     │ Business impact if test missing    │
│ Likelihood   │ 0-2     │ Probability of catching real bugs  │
│ Detection    │ 0-2     │ Early detection value              │
│ Efficiency   │ 0-2     │ Execution speed & reliability      │
│ Maintenance  │ 0-2     │ Cost to maintain (subtracted)      │
├──────────────┼─────────┼────────────────────────────────────┤
│ Total        │ 0-9     │ Higher = better test               │
└──────────────┴─────────┴────────────────────────────────────┘

Score Interpretation:
  7-9  ★★★  Essential — high-impact, efficient
  4-6  ★★   Good — solid coverage value
  1-3  ★    Review — may need improvement
  0    ✗    Consider removing or rewriting
```

## TDD Cycle (CORE-008)

```
  ┌─────────┐         ┌─────────┐         ┌──────────────┐
  │         │         │         │         │              │
  │   RED   │ ──────→ │  GREEN  │ ──────→ │   REFACTOR   │
  │         │         │         │         │              │
  │ Write   │         │ Write   │         │ Clean up     │
  │ failing │         │ minimum │         │ with all     │
  │ test    │         │ code to │         │ tests        │
  │         │         │ pass    │         │ passing      │
  └────┬────┘         └─────────┘         └──────┬───────┘
       │                                         │
       └─────────────────────────────────────────┘
                    repeat cycle
```

## Test Directory Structure

```
tests/
├── api/                  ← API layer tests
├── chaos/                ← Chaos engineering tests
├── cli/                  ← CLI interface tests
├── core/                 ← Core module tests
├── domain_orchestrators/ ← Domain orchestrator tests
├── golden/               ← 696 golden tests (regression-proof)
├── governance/           ← Governance rule tests
├── infrastructure/       ← Infrastructure layer tests
├── integration/          ← Cross-component integration tests
├── intelligence/         ← Intelligence layer tests
├── knowledge/            ← Knowledge base tests
├── lens/                 ← LENS analyzer tests
├── mcp/                  ← MCP tool tests
├── models/               ← Data model tests
├── observability/        ← Observability tests
├── orchestrators/        ← Orchestrator tests
├── performance/          ← Performance benchmarks
├── regression/           ← Regression tests
├── secrets/              ← Secret management tests
├── templates/            ← Template tests
├── testing/              ← Test framework meta-tests
├── tools/                ← Tool tests
├── unit/                 ← Unit tests
├── visualization/        ← Visualization tests
└── fixtures/             ← Shared test fixtures
```

---

*Verified against `tests/` directory and `pytest.ini` · 20 February 2026*
