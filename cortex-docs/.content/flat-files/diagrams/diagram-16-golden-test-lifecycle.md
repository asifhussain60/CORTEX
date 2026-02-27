# Golden Test Lifecycle — Scoring, Promotion, and Demotion
# The complete lifecycle from test creation through quality scoring to golden tier

```
                           ┌─────────────────────────────────────────────────┐
                           │            GOLDEN TEST LIFECYCLE                │
                           └─────────────────────────────────────────────────┘

 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │   CREATION   │────▶│   SCORING    │────▶│  PROMOTION   │────▶│ MAINTENANCE  │
 │  (RED Phase) │     │ (Quality Gate│     │ (→ Golden)   │     │ (Re-scoring) │
 └──────────────┘     └──────┬───────┘     └──────────────┘     └──────┬───────┘
                             │                                         │
                             ▼                                         ▼
                    ┌────────────────┐                         ┌────────────────┐
                    │  SCORE < 4:    │                         │  SCORE DROPS   │
                    │  DELETE        │                         │  BELOW 7:      │
                    │  (insufficient │                         │  DEMOTION      │
                    │   value)       │                         │  (back to unit)│
                    └────────────────┘                         └────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  QUALITY GATE SCORING (cortex/testing/quality_gate.py)
 ═══════════════════════════════════════════════════════════════════════════════

  Score = Impact(0─5) + Likelihood(0─3) + Detection(0─3) + Efficiency(0─2) − Maintenance(0─2)

  ┌─────────┬───────┬───────────────────────────────────────────────────────┐
  │  Range  │Verdict│ Action                                                │
  ├─────────┼───────┼───────────────────────────────────────────────────────┤
  │  ≥ 7    │ KEEP  │ Eligible for golden promotion                        │
  │  4 ─ 6  │REVIEW │ Needs improvement — may be refactored                │
  │  < 4    │DELETE │ Provides insufficient value — removed                │
  └─────────┴───────┴───────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  GOLDEN TEST ARCHITECTURE (tests/golden/ — 486 tests)
 ═══════════════════════════════════════════════════════════════════════════════

  tests/golden/
  ├── _golden_factory.py          ← GoldenScenario dataclass + registry
  ├── architecture/               ← Tier structure, OrchestratorMixin
  ├── audit_trail/                ← AC marker completeness
  ├── governance/                 ← CORE rule enforcement
  ├── integration/                ← E2E routing, MCP, LENS
  ├── holistic_integration/       ← S01─S25 scenario suite
  ├── orchestrators/              ← Per-orchestrator truth
  ├── production/                 ← Production readiness
  ├── routing/                    ← Intent differentiation
  ├── intelligence/               ← Scorer, unified brain
  ├── mcp/                        ← Tool registration
  ├── modes/                      ← Execution modes
  ├── phases/                     ← Phase-specific
  └── regression/                 ← Regression baselines


 ═══════════════════════════════════════════════════════════════════════════════
  URS FEEDBACK LOOP (Phase 83 — Unified Reinforcement Signal)
 ═══════════════════════════════════════════════════════════════════════════════

  Golden Test Outcome ───────────────────────▶ Reinforcement Signal
  ┌─────────────────────────┐                 ┌──────────────────┐
  │ All pass after refactor │ ────────────── ▶│ STRONG_REWARD +1 │
  │ Catches regression      │ ────────────── ▶│ DETECTION    +0.8│
  │ Becomes flaky           │ ────────────── ▶│ PUNISHMENT  −0.5 │
  │ Score drops < 7         │ ────────────── ▶│ DEMOTION    (0)  │
  └─────────────────────────┘                 └──────────────────┘
```

**Source:** `tests/golden/` · `cortex/testing/quality_gate.py` · `cortex-registry/core/test-quality-gate.yaml`
**Governance:** CORE-055 (Golden Test Tier Contract) — 486 golden tests must always pass
