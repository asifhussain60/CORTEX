# Audit Fix Pipeline — 9-Stage Flow
# The /audit fix command's complete stage pipeline

```
                                 /audit fix
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE -1: ENVIRONMENT READINESS                                     │
│  UpgradeOrchestrator.validate_requirements()                        │
│  • Python 3.9+ check                                                │
│  • requirements.txt → installed packages                            │
│  • P0 hard-stop if [PREFLIGHT CRITICAL] missing                     │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 0: INFLIGHT UPGRADE + PRE-FLIGHT                              │
│  • git fetch origin/main                                             │
│  • Merge if ahead                                                   │
│  • STAGE-0-GOVERNANCE-AUDIT-SPEC.md validation                      │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 1: GOVERNANCE PRE-FLIGHT                                      │
│  Full STAGE-0-GOVERNANCE-AUDIT-SPEC.md specification                 │
│  • Rule registry integrity                                          │
│  • Skull-rules.yaml parse                                           │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 2: 19-POINT PRODUCTION SCAN                                   │
│  cortex-auditor.md Checks #1–#19                                    │
│  • Orchestrator wiring (#1–#5)                                      │
│  • MCP tool health (#6–#8)                                          │
│  • Governance compliance (#9–#12)                                   │
│  • Intelligence coverage (#13–#15)                                  │
│  • Infrastructure health (#16–#18)                                  │
│  • SQLite activity log health (#19)                                 │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 3: WIRING CONTRACT VALIDATION                                 │
│  architecture-integrity-agent.md                                    │
│  • L1: Import graph validation                                      │
│  • L2: Protocol compliance (IOrchestrator)                          │
│  • L3: Cross-layer dependency checks                                │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 4: ORCHESTRATOR HEALTH (all 22 endpoints)                     │
│  HealthOrchestrator.run_health_check()                              │
│  • Each orchestrator's health endpoint pinged                       │
│  • Response time measured                                           │
│  • State validation                                                 │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 5: VACUUM CLEANUP                                             │
│  VacuumOrchestrator + cortex_vacuum                                 │
│  • Markdown sprawl detection                                        │
│  • Root clutter cleanup                                             │
│  • Archive stale artifacts                                          │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 6: PROMPT/AGENT META-AUDIT                                    │
│  cortex-meta-auditor.md (23 checks)                                 │
│  • Agent specification completeness                                 │
│  • Prompt consistency                                               │
│  • Cross-reference integrity                                        │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGES 7–8: AUTO-FIX CONVERGENCE LOOP                               │
│  detect-fix-rescan-loop primitive                                    │
│                                                                      │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐                    │
│    │ DETECT   │────→│   FIX    │────→│ RESCAN   │                    │
│    │ violations│     │ auto-fix │     │ validate │                    │
│    └──────────┘     └──────────┘     └────┬─────┘                    │
│                                           │                          │
│                                    P0=0 & P1=0?                      │
│                                     │         │                      │
│                                    YES        NO ──→ loop back       │
│                                     │                                │
│  CORE-064: loops until all P0/P1 resolved (not a single pass)       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 9: TESTS + AC_COMPLETE                                        │
│  python3 scripts/run_tests.py preflight                             │
│  • Preflight test suite (< 10s)                                     │
│  • SQLite cleanup (30-day retention + VACUUM)                       │
│  • AC_COMPLETE marker written                                       │
│  • Final status: ✅ ALL CLEAR or ❌ ISSUES REMAIN                   │
└──────────────────────────────────────────────────────────────────────┘
```
