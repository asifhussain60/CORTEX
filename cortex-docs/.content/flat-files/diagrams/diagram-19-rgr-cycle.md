# Red-Green-Refactor (RGR) Cycle — Looped Quality Enforcement
# Two-level RGR: Unit cycle per feature + Sweep cycle across codebase

```
 ═══════════════════════════════════════════════════════════════════════════════
  LEVEL 1: UNIT RGR — Per Feature/Fix (CORE-008)
 ═══════════════════════════════════════════════════════════════════════════════

  TDDOrchestrator (cortex/orchestrators/core/tdd_orchestrator.py)

                    ┌─────────────────────────────────────────┐
                    │         TDD CYCLE (per unit of work)     │
                    │                                         │
                    │    ┌───────┐                            │
                    │    │       │                            │
                    │    ▼       │                            │
                    │  ╔═══════╗ │                            │
                    │  ║  RED  ║ │  Write failing test first  │
                    │  ║       ║ │  Verify: test FAILS        │
                    │  ╚═══╤═══╝ │  (no implementation yet)   │
                    │      │     │                            │
                    │      ▼     │                            │
                    │  ╔═══════╗ │                            │
                    │  ║ GREEN ║ │  Write minimum code        │
                    │  ║       ║ │  Verify: test PASSES       │
                    │  ╚═══╤═══╝ │  (nothing extra)           │
                    │      │     │                            │
                    │      ▼     │                            │
                    │  ╔═══════════╗                          │
                    │  ║ REFACTOR  ║  Improve code            │
                    │  ║           ║  Verify: ALL tests PASS  │
                    │  ╚═══╤═══════╝  (no regressions)       │
                    │      │     │                            │
                    │      │     │  Score ≥ 7? ──▶ GOLDEN     │
                    │      ▼     │                            │
                    │  ┌─────────┐                            │
                    │  │VALIDATE │  Governance + audit trail  │
                    │  └─────────┘  URS signal emitted        │
                    └─────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  LEVEL 2: SWEEP RGR — Across Codebase (CORE-064)
 ═══════════════════════════════════════════════════════════════════════════════

  SweepCatalogueOrchestrator (cortex/orchestrators/support/sweep_catalogue_orchestrator.py)

  Problem detected: "Weak hashing in auth_service.py"

  ┌────────────────────────────────────────────────────────────────────────┐
  │                                                                        │
  │   ┌────────────┐     ┌──────────────────────────────┐                 │
  │   │ CATALOGUE  │────▶│ Scan ENTIRE codebase for ALL │                 │
  │   │            │     │ instances of same issue       │                 │
  │   └────────────┘     │                              │                 │
  │                      │ Found:                        │                 │
  │                      │  ✗ auth_service.py:42         │                 │
  │                      │  ✗ user_service.py:87         │                 │
  │                      │  ✗ legacy_utils.py:15         │                 │
  │                      └──────────────┬───────────────┘                 │
  │                                     │                                 │
  │                                     ▼                                 │
  │   ┌──────────────────────────────────────────────────────┐            │
  │   │  FOR EACH INSTANCE:                                  │            │
  │   │                                                      │            │
  │   │   RED ──▶ Write test for secure hashing              │            │
  │   │   GREEN ──▶ Replace weak hash with bcrypt            │            │
  │   │   REFACTOR ──▶ Extract shared hashing utility        │            │
  │   │                                                      │            │
  │   └──────────────────────────────────┬───────────────────┘            │
  │                                      │                                │
  │                                      ▼                                │
  │   ┌────────────┐     ┌──────────────────────────────┐                 │
  │   │  RESCAN    │────▶│ Zero remaining instances?     │                 │
  │   │            │     │                              │                 │
  │   └────────────┘     │  YES ──▶ Sweep COMPLETE ✅   │                 │
  │         ▲            │  NO  ──▶ Loop back ──────────┼──┐              │
  │         │            └──────────────────────────────┘  │              │
  │         └──────────────────────────────────────────────┘              │
  │                                                                        │
  └────────────────────────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  URS REINFORCEMENT — Closed-Loop Learning
 ═══════════════════════════════════════════════════════════════════════════════

  RGR Outcome                    Signal              Confidence Δ
  ┌────────────────────────┐     ┌────────────────┐  ┌──────────┐
  │ GREEN on first try     │────▶│ STRONG_REWARD  │──▶│   +1.0   │
  │ GREEN with retries     │────▶│ MILD_REWARD    │──▶│   +0.5   │
  │ Stuck in RED (3+)      │────▶│ MILD_PUNISHMENT│──▶│   −0.5   │
  │ Sweep completed        │────▶│ STRONG_REWARD  │──▶│   +1.0   │
  │ Sweep incomplete       │────▶│ STRONG_PUNISH  │──▶│   −1.0   │
  └────────────────────────┘     └────────────────┘  └──────────┘

  Confidence ≥ 0.9 ──▶ Pattern promoted to T1 knowledge
  Confidence ≤ 0.3 ──▶ Pattern quarantined
```

**Source:** `cortex/orchestrators/core/tdd_orchestrator.py` · `cortex/orchestrators/support/sweep_catalogue_orchestrator.py`
**Governance:** CORE-008 (TDD Mandatory), CORE-064 (Sweep Completeness Contract)
