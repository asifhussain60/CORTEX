# Testing Strategy — Pyramid, Execution Tiers, and Quality Gate
# Complete view of CORTEX testing architecture

```
                                        ▲
                                       ╱ ╲
                                      ╱   ╲
                                     ╱ 486 ╲
                                    ╱ GOLDEN╲                  GOLDEN: Must ALWAYS pass
                                   ╱  Tests  ╲                 Scored ≥7 on quality gate
                                  ╱───────────╲                Per-orchestrator truth tests
                                 ╱             ╲
                                ╱  Integration  ╲              INTEGRATION: Cross-component
                               ╱    Tests       ╲             E2E routing, MCP, LENS pipeline
                              ╱───────────────────╲
                             ╱                     ╲
                            ╱   ~15,000 Unit Tests  ╲          UNIT: Module-level isolation
                           ╱    (module-level)       ╲         Parallel: -n auto --dist loadscope
                          ╱───────────────────────────╲
                         ╱                             ╲
                        ╱      Smoke Tests (subset)     ╲      SMOKE: < 60s sanity gate
                       ╱─────────────────────────────────╲     Before every commit
                      ╱                                   ╲
                     ╱       Preflight (< 10s)             ╲   PREFLIGHT: Critical wiring only
                    ╱───────────────────────────────────────╲  /audit fix Stage 9


                    ┌───────────────────────────────────────────────────┐
                    │           EXECUTION MODES                        │
                    │                                                   │
                    │  ┌─────────┬────────────┬──────────────────────┐  │
                    │  │  Mode   │  Workers   │  Use Case            │  │
                    │  ├─────────┼────────────┼──────────────────────┤  │
                    │  │preflight│  serial    │  /audit fix Stage 9  │  │
                    │  │changed  │  testmon   │  TDD inner loop      │  │
                    │  │smoke    │  parallel  │  Sanity before commit│  │
                    │  │unit     │  parallel  │  Default local dev   │  │
                    │  │parallel │  -n auto   │  Pre-commit full     │  │
                    │  │golden   │  serial    │  Deterministic truth │  │
                    │  │integr.  │  -n 4      │  Cross-component     │  │
                    │  │batch    │  serial    │  CI gate             │  │
                    │  │healthchk│  parallel  │  Full on-demand      │  │
                    │  └─────────┴────────────┴──────────────────────┘  │
                    │                                                   │
                    │  Three Acceleration Layers:                       │
                    │  ┌─────────────────────────────────────────────┐  │
                    │  │ Layer 1: Parallel (pytest-xdist -n auto)   │  │
                    │  │ Layer 2: Smart (pytest-testmon, changed)    │  │
                    │  │ Layer 3: Import (importlib mode, -10s cold) │  │
                    │  └─────────────────────────────────────────────┘  │
                    └───────────────────────────────────────────────────┘


                    ┌───────────────────────────────────────────────────┐
                    │        TEST QUALITY GATE SCORING                  │
                    │                                                   │
                    │  Score = Impact + Likelihood + Detection +        │
                    │          Efficiency - Maintenance                 │
                    │                                                   │
                    │  ┌────────────────────────────────────────┐       │
                    │  │ 7-9  ★★★  Essential (KEEP)             │       │
                    │  │ 4-6  ★★   Good (REVIEW for upgrade)   │       │
                    │  │ 1-3  ★    Weak (REVIEW for rewrite)   │       │
                    │  │  0   ✗    Candidate for deletion      │       │
                    │  └────────────────────────────────────────┘       │
                    │                                                   │
                    │  Golden Promotion Requirements:                   │
                    │  • Score ≥ 7 on quality gate                     │
                    │  • ≥ 2 orchestrator references                   │
                    │  • ≥ 2 asserts per test function                 │
                    │  • Path matches tests/golden/                    │
                    └───────────────────────────────────────────────────┘
```
