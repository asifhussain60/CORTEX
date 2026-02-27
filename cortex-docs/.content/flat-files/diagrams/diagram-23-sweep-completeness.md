# Sweep Completeness — CORE-064 Lifecycle
# How the SweepCatalogueOrchestrator ensures no partial sweeps

```
 ═══════════════════════════════════════════════════════════════════════════════
  SWEEP COMPLETENESS CONTRACT — CORE-064
 ═══════════════════════════════════════════════════════════════════════════════

  SweepCatalogueOrchestrator (cortex/orchestrators/support/sweep_catalogue_orchestrator.py)

  "Every FIX/REFACTOR/AUDIT must exhaust its full issue catalogue.
   No partial sweeps. Ever."


                    ┌──────────────────────────────────────────────┐
                    │            ISSUE DETECTED                     │
                    │    "Weak hashing in auth_service.py"          │
                    └──────────────────┬───────────────────────────┘
                                       │
                                       ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │  STEP 1: CATALOGUE CREATION                                           │
  │                                                                        │
  │  SweepCatalogueOrchestrator scans ENTIRE codebase for ALL instances   │
  │                                                                        │
  │  ┌────────────────────────────────────────────────────────────┐        │
  │  │  SWEEP-084-WEAK-HASHING                                   │        │
  │  │  ┌──────────────────────────────────────────────────────┐  │        │
  │  │  │  Instance 1: auth_service.py:42     status: OPEN     │  │        │
  │  │  │  Instance 2: user_service.py:87     status: OPEN     │  │        │
  │  │  │  Instance 3: legacy_utils.py:15     status: OPEN     │  │        │
  │  │  └──────────────────────────────────────────────────────┘  │        │
  │  └────────────────────────────────────────────────────────────┘        │
  │                                                                        │
  │  Persisted to: .cortex-runtime/sweeps/{sweep_id}.db (SQLite WAL)      │
  └──────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │  STEP 2: FIX LOOP (per instance)                                      │
  │                                                                        │
  │  FOR EACH instance in catalogue:                                       │
  │    ┌─────┐    ┌───────┐    ┌──────────┐    ┌──────────┐              │
  │    │ RED │───▶│ GREEN │───▶│ REFACTOR │───▶│ VALIDATE │              │
  │    └─────┘    └───────┘    └──────────┘    └────┬─────┘              │
  │                                                  │                    │
  │    Instance status: OPEN ──▶ IN_PROGRESS ──▶ CLOSED                  │
  └──────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │  STEP 3: RESCAN                                                       │
  │                                                                        │
  │  Re-scan codebase for same issue pattern                               │
  │                                                                        │
  │  ┌─────────────────────────────────────────┐                          │
  │  │  All instances CLOSED?                   │                          │
  │  │                                         │                          │
  │  │  YES ──▶ Sweep COMPLETE                 │                          │
  │  │          Catalogue archived ✅           │                          │
  │  │                                         │                          │
  │  │  NO  ──▶ New instances found?           │                          │
  │  │          Add to catalogue               │                          │
  │  │          Loop back to STEP 2            │                          │
  │  └─────────────────────────────────────────┘                          │
  └────────────────────────────────────────────────────────────────────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  SWEEP CATALOGUE STATE MACHINE
 ═══════════════════════════════════════════════════════════════════════════════

  Sweep States:
  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐
  │ CREATED  │───▶│ IN_PROGRESS  │───▶│  COMPLETING  │───▶│ COMPLETE │
  └──────────┘    └──────┬───────┘    └──────────────┘    └──────────┘
                         │
                         │ (session ends before all fixed)
                         ▼
                  ┌──────────────┐
                  │   DURABLE    │  ← Persists across sessions
                  │  (SQLite WAL)│    Resumed on next session
                  └──────────────┘

  Instance States:
  ┌──────┐    ┌──────────────┐    ┌────────┐
  │ OPEN │───▶│ IN_PROGRESS  │───▶│ CLOSED │
  └──────┘    └──────────────┘    └────────┘


 ═══════════════════════════════════════════════════════════════════════════════
  INTEGRATION WITH /AUDIT FIX
 ═══════════════════════════════════════════════════════════════════════════════

  /audit fix Stages 7─8 use the detect-fix-rescan-loop primitive:

  Stage 2: Scan ──▶ Violations found (P0/P1/P2)
  Stage 7: Fix  ──▶ SweepCatalogueOrchestrator creates catalogues
  Stage 8: Loop ──▶ detect-fix-rescan-loop until p0==0 && p1==0
  Stage 9: Test ──▶ Verify all fixes pass tests

  Workflow Primitive: primitives/validation/detect-fix-rescan-loop.yaml
  Governance Primitives: primitives/governance/sweep-catalogue-open.yaml
                         primitives/governance/sweep-catalogue-close.yaml
```

**Source:** `cortex/orchestrators/support/sweep_catalogue_orchestrator.py` · `cortex-registry/workflows/templates/primitives/`
**Governance:** CORE-064 (Sweep Completeness Contract) — no partial sweeps, ever
